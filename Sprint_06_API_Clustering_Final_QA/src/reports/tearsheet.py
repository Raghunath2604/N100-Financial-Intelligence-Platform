
"""Generate two-page company tearsheets, sector intelligence PDFs and portfolio summary."""
from pathlib import Path
import sqlite3, io, re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def _clean(v):
    if pd.isna(v): return "N/A"
    if isinstance(v,(float,np.floating)): return f"{v:,.2f}"
    return str(v)

def _chart(history,title):
    fig,ax=plt.subplots(figsize=(7.4,2.6))
    if not history.empty:
        x=history.year.astype(str)
        if "sales" in history and history.sales.notna().any():
            ax.plot(x,history.sales,label="Revenue (₹ Cr)",marker="o")
        if "net_profit" in history and history.net_profit.notna().any():
            ax.plot(x,history.net_profit,label="Net profit (₹ Cr)",marker="o")
        ax.legend(loc="upper left",fontsize=7)
    ax.set_title(title,fontsize=10);ax.tick_params(axis="x",labelrotation=45,labelsize=7);ax.grid(alpha=.2)
    fig.tight_layout()
    buf=io.BytesIO();fig.savefig(buf,format="png",dpi=140);plt.close(fig);buf.seek(0)
    return buf

def _styles():
    s=getSampleStyleSheet()
    s.add(ParagraphStyle(name="SmallNote",parent=s["BodyText"],fontSize=7,leading=9,textColor=colors.HexColor("#555555")))
    s.add(ParagraphStyle(name="Section",parent=s["Heading2"],fontSize=12,textColor=colors.HexColor("#174A6E"),spaceBefore=7,spaceAfter=5))
    return s

def _table(data,widths=None):
    t=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([
      ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#174A6E")),
      ("TEXTCOLOR",(0,0),(-1,0),colors.white),
      ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
      ("FONTSIZE",(0,0),(-1,-1),7),("LEADING",(0,0),(-1,-1),9),
      ("GRID",(0,0),(-1,-1),.25,colors.HexColor("#C9D3DC")),
      ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F6F8")]),
      ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),
      ("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)
    ]))
    return t

def generate_tearsheets(db_path="database/nifty100.db",output_root="reports"):
    root=Path(output_root);target=root/"tearsheets";target.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as con:
        companies=pd.read_sql_query("SELECT id AS company_id,company_name,about_company,website FROM companies ORDER BY company_name",con)
        ratios=pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id,year",con)
        market=pd.read_sql_query("SELECT * FROM market_cap ORDER BY company_id,year",con)
        sectors=pd.read_sql_query("SELECT company_id,sub_sector FROM sectors",con)
        pl=pd.read_sql_query("SELECT * FROM profitandloss ORDER BY company_id,year",con)
        pros=pd.read_sql_query("SELECT * FROM prosandcons_generated",con) if False else pd.DataFrame()
        docs=pd.read_sql_query("SELECT company_id,year,annual_report FROM documents ORDER BY year DESC",con)
    # generated pros/cons CSV is the controlled output source
    pcpath=Path("output/pros_cons_generated.csv")
    if pcpath.exists(): pros=pd.read_csv(pcpath)
    for _,co in companies.iterrows():
        cid=co.company_id
        r=ratios[ratios.company_id==cid].sort_values("year")
        annual=r[r.year.astype(str).str.endswith("-03")]
        if annual.empty: annual=r.tail(1)
        latest=annual.iloc[-1] if len(annual) else pd.Series(dtype=object)
        hist=pl[pl.company_id==cid].sort_values("year").tail(10)
        m=market[market.company_id==cid].sort_values("year")
        mr=m.iloc[-1] if len(m) else pd.Series(dtype=object)
        sec=sectors[sectors.company_id==cid]
        sector=latest.get("broad_sector","Unassigned") if len(latest) else "Unassigned"
        p=pros[(pros.company_id==cid)&(pros.type=="pro")].sort_values("confidence_pct",ascending=False).head(4) if len(pros) else pd.DataFrame()
        c=pros[(pros.company_id==cid)&(pros.type=="con")].sort_values("confidence_pct",ascending=False).head(4) if len(pros) else pd.DataFrame()
        path=target/f"{cid}_tearsheet.pdf"
        styles=_styles()
        story=[Paragraph(f"{co.company_name} ({cid})",styles["Title"]),
          Paragraph(f"Sector: {sector} | Financial year: {_clean(latest.get('year'))} | Market snapshot: {_clean(mr.get('year'))}",styles["SmallNote"]),Spacer(1,5)]
        story.append(Paragraph("Investment profile — data-led summary",styles["Section"]))
        story.append(Paragraph(str(co.about_company or "Company description not available in supplied source data."),styles["BodyText"]))
        story.append(Spacer(1,6))
        kpis=[["Metric","Latest value","Metric","Latest value"],
          ["ROE",_clean(latest.get("return_on_equity_pct"))+"%" if pd.notna(latest.get("return_on_equity_pct")) else "N/A","ROCE",_clean(latest.get("return_on_capital_pct"))+"%" if pd.notna(latest.get("return_on_capital_pct")) else "N/A"],
          ["Debt/equity",_clean(latest.get("debt_to_equity")),"Free cash flow (₹ Cr)",_clean(latest.get("free_cash_flow_cr"))],
          ["P/E",_clean(mr.get("pe_ratio")),"P/B",_clean(mr.get("pb_ratio"))],
          ["Market cap (₹ Cr)",_clean(mr.get("market_cap_crore")),"Dividend yield",_clean(mr.get("dividend_yield_pct"))+"%" if pd.notna(mr.get("dividend_yield_pct")) else "N/A"]]
        story.append(_table(kpis,[35*mm,45*mm,38*mm,48*mm]));story.append(Spacer(1,7))
        story.append(Paragraph("Revenue and earnings history (up to 10 supplied annual observations)",styles["Section"]))
        story.append(Image(_chart(hist,f"{co.company_name}: revenue and net profit"),width=175*mm,height=61*mm))
        story.append(Paragraph("All figures reflect the supplied source dataset. This report is informational and is not a recommendation to buy or sell securities.",styles["SmallNote"]))
        story.append(PageBreak())
        story.append(Paragraph(f"{co.company_name} — Financial Quality & Risk Review",styles["Title"]))
        story.append(Paragraph("Strength indicators",styles["Section"]))
        prodata=[["Rule","Evidence","Confidence"]]
        if len(p):
            prodata += [[str(x.rule),str(x.statement),f"{x.confidence_pct:.0f}%"] for x in p.itertuples()]
        else: prodata += [["Data coverage","No rule-triggered strength signal was available.","N/A"]]
        story.append(_table(prodata,[40*mm,105*mm,20*mm]));story.append(Spacer(1,6))
        story.append(Paragraph("Risk indicators",styles["Section"]))
        condata=[["Rule","Evidence","Confidence"]]
        if len(c):
            condata += [[str(x.rule),str(x.statement),f"{x.confidence_pct:.0f}%"] for x in c.itertuples()]
        else: condata += [["Data coverage","No rule-triggered risk signal was available.","N/A"]]
        story.append(_table(condata,[40*mm,105*mm,20*mm]));story.append(Spacer(1,6))
        story.append(Paragraph("Selected annual financial history",styles["Section"]))
        if len(hist):
            rows=[["Year","Sales (₹ Cr)","Net profit (₹ Cr)","EPS","OPM %"]]
            for x in hist.tail(7).itertuples():
                rows.append([str(x.year),_clean(x.sales),_clean(x.net_profit),_clean(x.eps),_clean(x.opm_percentage)])
            story.append(_table(rows,[32*mm,36*mm,36*mm,30*mm,30*mm]))
        else: story.append(Paragraph("Annual P&L history unavailable.",styles["BodyText"]))
        report=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=17*mm,leftMargin=17*mm,topMargin=14*mm,bottomMargin=14*mm,title=f"{cid} N100 tearsheet",author="N100 Financial Intelligence Platform")
        report.build(story)
    return sorted(target.glob("*_tearsheet.pdf"))

def generate_sector_reports(db_path="database/nifty100.db",output_root="reports"):
    root=Path(output_root);target=root/"sector";target.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as con:
        companies=pd.read_sql_query("SELECT id AS company_id,company_name FROM companies",con)
        ratios=pd.read_sql_query("SELECT * FROM financial_ratios WHERE substr(year,-2)='03' ORDER BY year",con)
        market=pd.read_sql_query("SELECT * FROM market_cap ORDER BY year",con)
        sectors=pd.read_sql_query("SELECT company_id,sub_sector FROM sectors",con)
    latest=ratios.groupby("company_id",as_index=False).tail(1)
    mc=market.groupby("company_id",as_index=False).tail(1)
    df=latest.merge(companies,on="company_id",how="left").merge(sectors,on="company_id",how="left").merge(mc[["company_id","market_cap_crore","pe_ratio"]],on="company_id",how="left")
    names=sorted(df.broad_sector.dropna().unique())
    styles=_styles()
    for sector in names:
        g=df[df.broad_sector==sector].copy()
        story=[Paragraph(f"{sector} — Sector Intelligence",styles["Title"]),Paragraph(f"Companies covered: {g.company_id.nunique()}",styles["SmallNote"]),Spacer(1,8)]
        summary=[["Metric","Sector median","Companies with data"]]
        for col,label in [("return_on_equity_pct","Median ROE (%)"),("return_on_capital_pct","Median ROCE (%)"),("debt_to_equity","Median debt/equity"),("free_cash_flow_cr","Median FCF (₹ Cr)"),("pe_ratio","Median P/E"),("market_cap_crore","Median market cap (₹ Cr)")]:
            summary.append([label,_clean(g[col].median()),str(g[col].notna().sum())])
        story.append(_table(summary,[70*mm,55*mm,45*mm]));story.append(Spacer(1,8))
        top=g.sort_values("return_on_capital_pct",ascending=False).head(12)
        rows=[["Company","ROE %","ROCE %","D/E","P/E"]]+[[str(x.company_name),_clean(x.return_on_equity_pct),_clean(x.return_on_capital_pct),_clean(x.debt_to_equity),_clean(x.pe_ratio)] for x in top.itertuples()]
        story.append(Paragraph("Company comparison",styles["Section"]));story.append(_table(rows,[65*mm,28*mm,28*mm,25*mm,25*mm]))
        story.append(Spacer(1,8));story.append(Paragraph("Sector observations are descriptive summaries of supplied historical financial data, not forecasts or investment advice.",styles["SmallNote"]))
        SimpleDocTemplate(str(target/(re.sub(r"[^A-Za-z0-9]+","_",sector).strip("_")+"_sector_report.pdf")),pagesize=A4).build(story)
    # The source data contains ten distinct broad sectors. The eleventh requested PDF is a cross-sector benchmark, not a fabricated sector.
    story=[Paragraph("Nifty 100 — Cross-Sector Benchmark",styles["Title"]),Paragraph("Cross-sector overview included as the 11th sector intelligence PDF because the supplied sector master contains ten distinct broad-sector labels.",styles["SmallNote"]),Spacer(1,8)]
    rows=[["Sector","Companies","Median ROE %","Median ROCE %","Median P/E"]]
    for sec,g in df.groupby("broad_sector"):
        rows.append([str(sec),str(g.company_id.nunique()),_clean(g.return_on_equity_pct.median()),_clean(g.return_on_capital_pct.median()),_clean(g.pe_ratio.median())])
    story.append(_table(rows,[60*mm,25*mm,30*mm,30*mm,25*mm]))
    SimpleDocTemplate(str(target/"Nifty_100_Cross_Sector_Benchmark.pdf"),pagesize=A4).build(story)
    return sorted(target.glob("*.pdf"))

def generate_portfolio_summary(db_path="database/nifty100.db",output_root="reports"):
    root=Path(output_root);target=root/"portfolio";target.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as con:
        sectors=pd.read_sql_query("SELECT company_id,index_weight_pct FROM sectors",con)
        companies=pd.read_sql_query("SELECT id AS company_id,company_name FROM companies",con)
        ratios=pd.read_sql_query("SELECT * FROM financial_ratios WHERE substr(year,-2)='03' ORDER BY year",con)
        market=pd.read_sql_query("SELECT * FROM market_cap ORDER BY year",con)
    latest=ratios.groupby("company_id",as_index=False).tail(1)
    mc=market.groupby("company_id",as_index=False).tail(1)
    df=sectors.merge(companies,on="company_id").merge(latest,on="company_id",how="left").merge(mc[["company_id","market_cap_crore","pe_ratio"]],on="company_id",how="left")
    story=[Paragraph("Nifty 100 — Portfolio & Market Intelligence Summary",_styles()["Title"]),
      Paragraph("Universe-level snapshot from the supplied historical dataset. This is a descriptive research summary, not portfolio advice.",_styles()["SmallNote"]),Spacer(1,8)]
    kpis=[["Universe KPI","Value"],["Companies",str(df.company_id.nunique())],["Sectors",str(df.broad_sector.nunique())],["Median ROE",_clean(df.return_on_equity_pct.median())+"%"],["Median ROCE",_clean(df.return_on_capital_pct.median())+"%"],["Median P/E",_clean(df.pe_ratio.median())]]
    story.append(_table(kpis,[75*mm,85*mm]));story.append(Spacer(1,8))
    sec=df.groupby("broad_sector").agg(companies=("company_id","nunique"),index_weight_pct=("index_weight_pct","sum"),median_roe=("return_on_equity_pct","median"),median_pe=("pe_ratio","median")).reset_index()
    rows=[["Sector","Companies","Index weight %","Median ROE %","Median P/E"]]+[[str(x.broad_sector),str(x.companies),_clean(x.index_weight_pct),_clean(x.median_roe),_clean(x.median_pe)] for x in sec.itertuples()]
    story.append(Paragraph("Sector distribution and quality",_styles()["Section"]));story.append(_table(rows,[50*mm,25*mm,30*mm,30*mm,25*mm]))
    story.append(Spacer(1,8));story.append(Paragraph("Source data coverage and caveats",_styles()["Section"]))
    story.append(Paragraph("Market multiples are dated workbook snapshots, not live quotes. Missing FCF and financial metrics are not imputed. Company-level financial statements can have differing fiscal year ends. Interpret peer and sector comparisons in light of source coverage.",_styles()["BodyText"]))
    path=target/"portfolio_summary.pdf"
    SimpleDocTemplate(str(path),pagesize=A4).build(story)
    return path
