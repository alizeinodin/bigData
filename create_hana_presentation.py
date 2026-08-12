#!/usr/bin/env python3
"""Generate Persian PowerPoint from SAP S/4HANA in-memory computing article."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

FONT_NAME = "Noto Naskh Arabic"
TITLE_COLOR = RGBColor(0, 51, 102)
ACCENT_COLOR = RGBColor(0, 102, 153)
BODY_COLOR = RGBColor(40, 40, 40)


def set_rtl(paragraph):
    try:
        from pptx.oxml.ns import qn
        pPr = paragraph._p.get_or_add_pPr()
        pPr.set(qn("a:rtl"), "1")
    except Exception:
        pass


def add_title_slide(prs, title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor(245, 248, 252)

    box = slide.shapes.add_textbox(Inches(0.5), Inches(2.0), Inches(9), Inches(1.8))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_NAME
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TITLE_COLOR
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.0), Inches(9), Inches(2.5))
        stf = sub_box.text_frame
        stf.word_wrap = True
        sp = stf.paragraphs[0]
        sp.text = subtitle
        sp.font.name = FONT_NAME
        sp.font.size = Pt(18)
        sp.font.color.rgb = ACCENT_COLOR
        sp.alignment = PP_ALIGN.CENTER
        set_rtl(sp)


def add_section_slide(prs, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = TITLE_COLOR

    box = slide.shapes.add_textbox(Inches(0.5), Inches(3.0), Inches(9), Inches(1.2))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_NAME
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)


def add_content_slide(prs, title, bullets, sub_bullets=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.3), Inches(9.2), Inches(0.8))
    tp = title_box.text_frame.paragraphs[0]
    tp.text = title
    tp.font.name = FONT_NAME
    tp.font.size = Pt(26)
    tp.font.bold = True
    tp.font.color.rgb = TITLE_COLOR
    tp.alignment = PP_ALIGN.RIGHT
    set_rtl(tp)

    line = slide.shapes.add_shape(1, Inches(0.4), Inches(1.05), Inches(9.2), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_COLOR
    line.line.fill.background()

    body_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9.0), Inches(5.8))
    tf = body_box.text_frame
    tf.word_wrap = True

    sub_bullets = sub_bullets or {}

    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + bullet
        p.font.name = FONT_NAME
        p.font.size = Pt(17)
        p.font.color.rgb = BODY_COLOR
        p.alignment = PP_ALIGN.RIGHT
        p.space_after = Pt(8)
        p.level = 0
        set_rtl(p)

        if bullet in sub_bullets:
            for sub in sub_bullets[bullet]:
                sp = tf.add_paragraph()
                sp.text = "  ◦ " + sub
                sp.font.name = FONT_NAME
                sp.font.size = Pt(15)
                sp.font.color.rgb = RGBColor(70, 70, 70)
                sp.alignment = PP_ALIGN.RIGHT
                sp.level = 1
                set_rtl(sp)


def add_table_slide(prs, title, headers, rows):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.3), Inches(9.2), Inches(0.7))
    tp = title_box.text_frame.paragraphs[0]
    tp.text = title
    tp.font.name = FONT_NAME
    tp.font.size = Pt(22)
    tp.font.bold = True
    tp.font.color.rgb = TITLE_COLOR
    tp.alignment = PP_ALIGN.RIGHT
    set_rtl(tp)

    cols = len(headers)
    table_rows = len(rows) + 1
    table = slide.shapes.add_table(table_rows, cols, Inches(0.3), Inches(1.1), Inches(9.4), Inches(5.8)).table

    col_width = Inches(9.4 / cols)
    for c in range(cols):
        table.columns[c].width = col_width

    for c, header in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = header
        for p in cell.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            set_rtl(p)
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT_COLOR

    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.name = FONT_NAME
                p.font.size = Pt(11)
                p.font.color.rgb = BODY_COLOR
                p.alignment = PP_ALIGN.CENTER
                set_rtl(p)
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(240, 245, 250)


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "محاسبات درون‌حافظه‌ای با کارایی بالا",
        "بررسی پژوهشی لایه پایگاه‌داده SAP S/4HANA\n\n"
        "درس: پایگاه‌داده پیشرفته (کارشناسی ارشد)\n"
        "منبع: Raikar, T. (2025) — American Journal of Technology\n"
        "DOI: 10.58425/ajt.v4i2.449",
    )

    add_content_slide(
        prs,
        "چکیده",
        [
            "هدف: بررسی چگونگی دستیابی SAP S/4HANA به سرعت پردازش فوق‌العاده از طریق معماری درون‌حافظه‌ای",
            "روش: مطالعه مستندات SAP HANA، اجرای کوئری‌های SQL، CDS Views و SQL Script، و تحلیل با ابزارهای ST05، ST12، SAT، DBACOCKPIT و PlanViz",
            "یافته‌ها: ذخیره‌سازی ستونی، فشرده‌سازی Dictionary/Vector، پردازش Set-based، ایندکس‌گذاری و پارتیشن‌بندی کارایی را به‌شدت افزایش می‌دهند",
            "نتیجه: ترکیب طراحی درون‌حافظه‌ای با بهینه‌سازی‌های لایه پایگاه‌داده، پایه پردازش بلادرنگ S/4HANA است",
        ],
    )

    add_content_slide(
        prs,
        "کلمات کلیدی",
        [
            "SAP S/4HANA",
            "محاسبات درون‌حافظه‌ای (In-Memory Computing)",
            "بهینه‌سازی کارایی پایگاه‌داده",
            "تحلیل بلادرنگ (Real-time Analytics)",
            "ذخیره‌سازی ستونی (Columnar Storage)",
            "پردازش Set-based و Push-down",
            "پردازش موازی و پارتیشن‌بندی جداول",
        ],
    )

    add_section_slide(prs, "۱. مقدمه")

    add_content_slide(
        prs,
        "چرا لایه پایگاه‌داده مهم است؟",
        [
            "کارایی SAP S/4HANA تحت تأثیر سه لایه وابسته به هم است: پایگاه‌داده، کاربرد (Application) و زیرساخت",
            "در پایگاه‌داده‌های سنتی، هر کوئری تأخیر I/O دیسک ایجاد می‌کند",
            "S/4HANA کل جداول، ایندکس‌ها و نتایج میانی را در RAM نگه می‌دارد و فقط برای پایداری گاه‌به‌گاه روی دیسک می‌نویسد",
            "دسترسی به داده در میکروثانیه (به‌جای میلی‌ثانیه) تحول بنیادینی در پردازش بارهای سازمانی ایجاد می‌کند",
            "معماری HTAP امکان اجرای همزمان تراکنش (OLTP) و تحلیل (OLAP) را بدون ETL فراهم می‌کند",
        ],
    )

    add_content_slide(
        prs,
        "معماری SAP S/4HANA",
        [
            "Connection & Session Management: مدیریت اتصال و نشست کاربران",
            "Calculation Engine: پردازش کوئری‌های SQL، SQL Script و MDX",
            "Optimizer & Plan Generator: یافتن سریع‌ترین مسیر اجرا",
            "In-Memory Processing Engines:",
            "Persistence Layer: ثبت لاگ، بازیابی و ذخیره‌سازی پایدار",
        ],
        sub_bullets={
            "In-Memory Processing Engines:": [
                "Column/Row Engine — داده ساخت‌یافته",
                "Graph Engine — روابط و سلسله‌مراتب",
                "Text Engine — جستجوی متنی",
            ]
        },
    )

    add_section_slide(prs, "۲. مرور ادبیات")

    add_content_slide(
        prs,
        "پژوهش‌های پیشین",
        [
            "Zhang Mei (2024): بهره‌گیری از مدل درون‌حافظه HANA برای تحلیل بلادرنگ و کاهش افزونگی",
            "IRJMETS (2022/2025): تکنیک‌های partition pruning، push-down projection و data tiering",
            "Müller et al. (2015): بهینه‌سازی join با aggregate cache و object-awareness",
            "Plattner (2014): پایه نظری column store، فشرده‌سازی و pushdown در مدیریت داده درون‌حافظه‌ای",
        ],
    )

    add_content_slide(
        prs,
        "شکاف‌های پژوهشی",
        [
            "بیشتر مطالعات ویژگی‌ها را توضیح می‌دهند اما معیارهای واقعی runtime در S/4HANA ارائه نمی‌کنند",
            "تأثیر indexing و partitioning روی بارهای کاری مختلف به‌طور کمی بررسی نشده",
            "ابزارهای SAP مانند ST05، PlanViz و DBACOCKPIT کمتر در ادبیات استفاده شده‌اند",
            "چارچوب یکپارچه‌ای برای تعامل query design، compression، indexing و partitioning وجود ندارد",
            "این مقاله با رویکرد عملی این شکاف‌ها را پر می‌کند",
        ],
    )

    add_section_slide(prs, "۳. روش‌شناسی")

    add_content_slide(
        prs,
        "روش پژوهش",
        [
            "مبتنی بر مستندات SAP HANA، راهنمای توسعه S/4HANA و ادبیات HTAP",
            "آزمایش عملی با SQL، CDS Views و SQL Script روی SAP HANA",
            "مقایسه منطق ABAP مبتنی بر حلقه (Loop) با اجرای Set-based در پایگاه‌داده",
            "ابزارهای تحلیل: ST05، ST12، SAT، DBACOCKPIT، PlanViz",
            "بررسی execution plan، CPU usage، scan volume و رفتار parallel processing",
        ],
    )

    add_section_slide(prs, "۴. اصول مدیریت داده درون‌حافظه‌ای")

    add_content_slide(
        prs,
        "ذخیره‌سازی ستونی (Column Store)",
        [
            "برخلاف Row Store، داده‌ها ستون‌به‌ستون ذخیره می‌شوند",
            "فقط ستون‌های مورد نیاز کوئری خوانده می‌شوند → کاهش شدید I/O",
            "Dictionary Encoding: مقادیر یکتا در جدول lookup نگهداری می‌شوند",
            "Vector Encoding: به‌جای مقدار خام، ValueID از dictionary ذخیره می‌شود",
            "نتیجه: مصرف RAM کمتر و دسترسی سریع‌تر به داده",
        ],
    )

    add_table_slide(
        prs,
        "مزایای ذخیره‌سازی ستونی",
        ["بهینه‌سازی", "بهبود سرعت"],
        [
            ["Column Store — داده اسکن‌شده", "۸۰–۹۵٪ کاهش"],
            ["Dictionary Encoding", "۳ برابر سریع‌تر"],
            ["Vector Encoding", "۳–۶ برابر سریع‌تر"],
            ["فشرده‌سازی", "۳–۱۰ برابر کوچک‌تر"],
            ["SUM/Aggregation Pushdown", "۶۰–۸۰٪ سریع‌تر"],
            ["Parallel Column Scans", "۵–۱۶ برابر سریع‌تر"],
        ],
    )

    add_content_slide(
        prs,
        "مقایسه Row Store و Column Store",
        [
            "جدول ORDERS با ۱۰۰ میلیون سطر — کوئری: SUM(Amount) WHERE Country='IN'",
            "Row Store (اسکن کامل): ≈ ۷.۲ GB خوانده می‌شود؛ ۹۰٪ بی‌فایده",
            "Row Store (با B-tree index): ≈ ۳۶۰ MB + overhead دسترسی تصادفی",
            "Column Store: فقط ستون‌های Country (≈100 MB) + Amount (≈800 MB) ≈ ۹۰۰ MB",
            "Column Store حدود ۸ برابر سریع‌تر و CPU-friendlyتر است",
        ],
    )

    add_content_slide(
        prs,
        "پردازش موازی (Parallel Processing)",
        [
            "استفاده از multi-core CPU و distributed nodes در SAP HANA",
            "تقسیم کوئری به subtaskهای همزمان (مثلاً هر منطقه جغرافیایی روی یک core)",
            "اسکن ستونی موازی: ۵–۱۶ برابر سریع‌تر",
            "تجمیع موازی: ۴–۱۲ برابر سریع‌تر",
            "Join موازی: ۳–۱۰ برابر سریع‌تر — runtime از دقیقه به ثانیه",
        ],
    )

    add_table_slide(
        prs,
        "HTAP: ترکیب OLTP و OLAP",
        ["حوزه", "ECC سنتی", "SAP HANA (HTAP)", "بهبود"],
        [
            ["گزارش عملیاتی", "تأخیر ساعتی/روزانه", "۰–۱ ثانیه", "تا ۱۰۰۰×"],
            ["ETL/Batch", "شبانه/ساعتی", "حذف کامل", "۱۰۰٪"],
            ["زمان کوئری تحلیلی", "۱۰–۳۰۰ ثانیه", "۰.۱–۱.۵ ثانیه", "۲۰–۲۰۰×"],
            ["Dashboard بلادرنگ", "بعد از ETL", "فوری", "بلادرنگ"],
            ["پیچیدگی landscape", "ECC+BW+ETL", "یک پایگاه HANA", "۴۰–۶۰٪ کمتر"],
        ],
    )

    add_section_slide(prs, "۵. Push-Down Processing")

    add_content_slide(
        prs,
        "پردازش Push-Down چیست؟",
        [
            "در SAP سنتی: منطق کسب‌وکار در Application Server (ABAP) اجرا می‌شد",
            "داده خام از DB به App Server منتقل و در حلقه پردازش می‌شد → بار شبکه بالا",
            "S/4HANA: محاسبات به لایه پایگاه‌داده «فرو رانده» می‌شوند",
            "HANA تجمیع، join و filter را درون حافظه انجام می‌دهد",
            "فقط نتیجه نهایی (نه داده خام) به App Server برمی‌گردد — کاهش ۸۰–۹۵٪ انتقال داده",
        ],
    )

    add_content_slide(
        prs,
        "طراحی کوئری (Query Design)",
        [
            "به‌جای ABAP Loop از Join، CDS View و Set-based logic استفاده کنید",
            "CDS Views: Interface (I_)، Composite (C_)، Consumption (Z_/Y_)",
            "فیلتر را زود اعمال کنید (WHERE قبل از HAVING)",
            "از Window Functions استفاده کنید: ROW_NUMBER، RANK، LEAD، LAG",
            "اصول Clean Core: namespace Z/Y، Extension Views، Adapt before Build",
        ],
    )

    add_table_slide(
        prs,
        "مزایای بهینه‌سازی کوئری",
        ["حوزه", "ECC / ABAP", "HANA Push-Down", "بهبود"],
        [
            ["حجم انتقال داده", "داده خام زیاد", "فقط نتیجه فیلتر/تجمیع", "۸۰–۹۵٪"],
            ["محاسبات حلقه‌ای", "App Server", "Vectorized در HANA", "۱۰–۵۰×"],
            ["Aggregations", "Loop در ABAP", "Columnar در RAM", "۲۰–۶۰×"],
            ["Joins", "SELECT SINGLE متعدد", "Parallel join در HANA", "۵–۳۰×"],
            ["Filters", "Boolean در ABAP", "ValueID pushdown", "۵–۲۰×"],
        ],
    )

    add_content_slide(
        prs,
        "ایندکس‌گذاری (Indexing)",
        [
            "Dictionary encoding خود به‌نوعی index سبک است",
            "Inverted Index: نگاشت ValueID → Row IDs (جستجوی سریع)",
            "Full-Text Index: جستجوی متنی با حذف stop words",
            "Multi-Column Index: dictionary ترکیبی برای چند ستون",
            "انواع: Inverted Value، Inverted Hash، Inverted Individual",
        ],
    )

    add_content_slide(
        prs,
        "بهترین شیوه‌های Index",
        [
            "Inverted Value: سریع‌ترین read/join — برای PK و unique constraints",
            "Inverted Hash: کاهش ≈۳۰٪ حافظه — برای PK با ستون‌های بلند",
            "Inverted Individual: DML سریع‌تر — read کمی کندتر (۱۰–۲۰٪)",
            "Composite key: ستون‌های selective اول، سپس equality، سپس range",
            "از index روی ستون‌های low-selectivity (Boolean/status) خودداری کنید",
            "فقط وقتی index بسازید که Expensive Statement Trace نیاز را نشان دهد",
        ],
    )

    add_content_slide(
        prs,
        "پارتیشن‌بندی جداول (Table Partitioning)",
        [
            "Hash Partitioning: توزیع یکنواخت بر اساس hash کلید — مناسب CUSTOMER_ID",
            "Round-Robin: توزیع چرخشی — مناسب staging/ETL، نه lookup انتخابی",
            "Range Partitioning: بر اساس بازه (مثلاً FISCAL_YEAR) — partition pruning",
            "Hash: عبور از محدودیت ۲ میلیارد سطر + parallel scan روی nodes",
            "Range: ایده‌آل برای داده سری‌زمانی (CALMONTH، DOC_DATE)",
        ],
    )

    add_table_slide(
        prs,
        "مزایای پارتیشن‌بندی",
        ["حوزه", "ECC", "SAP HANA", "بهبود"],
        [
            ["Range Query", "اسکن کل جدول", "فقط partition مرتبط", "تا ۹۵٪ کمتر"],
            ["Parallel Processing", "تک‌رشته‌ای", "هر partition روی core جدا", "۵–۲۵×"],
            ["Join & Aggregate", "روی کل جدول", "Partition-wise موازی", "۳–۱۵×"],
        ],
    )

    add_section_slide(prs, "۶. نتیجه‌گیری")

    add_content_slide(
        prs,
        "نتیجه‌گیری",
        [
            "معماری درون‌حافظه S/4HANA با column store، compression، parallel processing و HTAP کارایی را متحول می‌کند",
            "Push-down، indexing و partitioning باید به‌صورت یکپارچه در طراحی سیستم لحاظ شوند",
            "انتقال محاسبات از ABAP Loop به CDS/SQL Script کاهش چشمگیر runtime و network load دارد",
            "ابزارهای trace (ST05، PlanViz، ...) برای tuning عملی ضروری هستند",
            "پژوهش‌های آینده: سناریوهای صنعتی، cloud multi-tenant و بارهای AI",
        ],
    )

    add_content_slide(
        prs,
        "توصیه‌های عملی",
        [
            "برنامه‌نویسی Set-based را به push-down در پایگاه‌داده ترجیح دهید",
            "Indexing و partitioning را متناسب با الگوی workload طراحی کنید",
            "CDS Views لایه‌بندی‌شده و Clean Core را رعایت کنید",
            "Performance engineering را در چرخه پیاده‌سازی بگنجانید",
            "از HTAP برای حذف ETL و dashboard بلادرنگ روی داده عملیاتی بهره ببرید",
        ],
    )

    add_content_slide(
        prs,
        "منابع و اختصارات",
        [
            "CDS: Core Data Services | RAM: Random Access Memory",
            "OLTP: Online Transaction Processing | OLAP: Online Analytical Processing",
            "ETL: Extract, Transform, Load | HTAP: Hybrid Transactional/Analytical Processing",
            "Raikar, T. (2025). High-Performance In-Memory Computing: A Research Study on SAP S/4 HANA Database Layer. American Journal of Technology, 4(2), 94–113.",
            "DOI: https://doi.org/10.58425/ajt.v4i2.449",
        ],
    )

    add_title_slide(
        prs,
        "سپاس از توجه شما",
        "سوالات؟",
    )

    return prs


if __name__ == "__main__":
    output = "/workspace/SAP_S4HANA_InMemory_Presentation_FA.pptx"
    presentation = build_presentation()
    presentation.save(output)
    print(f"Saved: {output}")
    print(f"Slides: {len(presentation.slides)}")
