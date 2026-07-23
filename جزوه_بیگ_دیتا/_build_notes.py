# -*- coding: utf-8 -*-
"""Build Word-style Big Data exam notes with correct page index."""
from pathlib import Path
from weasyprint import HTML, CSS as WCSS
import fitz, shutil

OUT = Path('/workspace/جزوه_بیگ_دیتا')
ART = Path('/opt/cursor/artifacts')

CSS = r'''
@page {
  size: A4;
  margin: 1.1cm 1cm 1.4cm 1cm;
  @bottom-center {
    content: "صفحه " counter(page);
    font-size: 9pt; color: #4a5568; direction: rtl;
  }
}
body {
  direction: rtl;
  font-family: "DejaVu Sans", Tahoma, sans-serif;
  font-size: 10pt; line-height: 1.48; color: #1a202c;
}
h1 {
  font-size: 1.28rem; color: #1a365d; border-bottom: 3px solid #2b6cb0;
  padding-bottom: .2rem; margin: 0 0 .4rem;
}
h2 {
  font-size: 1.05rem; color: #1a365d; background: #ebf8ff;
  border-right: 5px solid #2b6cb0; padding: .24rem .45rem;
  margin: .85rem 0 .3rem; page-break-after: avoid;
}
h3 {
  font-size: .96rem; color: #2c5282; margin: .5rem 0 .2rem; page-break-after: avoid;
}
p { margin: .22rem 0; text-align: justify; }
ul, ol { margin: .2rem 0; padding-right: 1.05rem; }
li { margin: .08rem 0; }
table {
  border-collapse: collapse; width: 100%; margin: .28rem 0 .4rem;
  font-size: 8.8pt; page-break-inside: avoid;
}
th, td {
  border: 1px solid #a0aec0; padding: .18rem .3rem; text-align: right; vertical-align: top;
}
th { background: #90cdf4; color: #1a365d; }
tr:nth-child(even) td { background: #f7fafc; }
.note {
  background: #fffaf0; border-right: 4px solid #dd6b20; padding: .3rem .42rem;
  margin: .3rem 0; color: #7b341e; page-break-inside: avoid;
}
.meta { color: #2d3748; margin-bottom: .35rem; font-size: 9.2pt; }
/* Word-like formula box: FORCE LTR, no mirroring */
.eq {
  direction: ltr !important;
  unicode-bidi: bidi-override !important;
  text-align: center;
  background: #edf2f7;
  border: 2px solid #2d3748;
  border-radius: 6px;
  padding: .55rem .7rem;
  margin: .4rem 0 .3rem;
  font-family: "DejaVu Sans", "Times New Roman", serif;
  font-size: 14pt;
  font-weight: 700;
  page-break-inside: avoid;
  line-height: 1.7;
  letter-spacing: 0.02em;
}
.eq .line { display: block; margin: .12rem 0; }
.where {
  direction: rtl !important;
  unicode-bidi: embed !important;
  text-align: right;
  font-size: 9pt; font-weight: 400; color: #2d3748;
  margin-top: .35rem; border-top: 1px dashed #a0aec0; padding-top: .28rem;
  font-family: "DejaVu Sans", Tahoma, sans-serif;
}
.where div { margin: .05rem 0; }
.ex {
  background: #f0fff4; border: 1px solid #68d391; border-right: 4px solid #38a169;
  padding: .38rem .48rem; margin: .32rem 0 .4rem; border-radius: 4px;
  page-break-inside: avoid;
}
.ex .title { font-weight: bold; color: #276749; margin-bottom: .18rem; }
.ex .step { margin: .12rem 0; }
.ex .calc {
  direction: ltr !important;
  unicode-bidi: bidi-override !important;
  text-align: left;
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 9.4pt;
  background: #fff; border: 1px solid #c6f6d5;
  padding: .28rem .4rem; margin: .16rem 0;
  white-space: pre-wrap; border-radius: 3px;
}
.ans {
  background: #ebf8ff; border: 1px solid #63b3ed; padding: .2rem .32rem;
  margin-top: .18rem; font-weight: bold; color: #2c5282;
}
.small { font-size: 8.5pt; color: #4a5568; }
.mark {
  direction: ltr; unicode-bidi: bidi-override;
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8pt; color: #718096;
}
hr { border: none; border-top: 1px dashed #a0aec0; margin: .55rem 0; }
'''


def eq(lines, where=None):
    L = ''.join(f'<span class="line">{x}</span>' for x in lines)
    w = ''
    if where:
        w = ('<div class="where"><b>که در آن:</b>'
             + ''.join(f'<div>{i}</div>' for i in where) + '</div>')
    return f'<div class="eq">{L}{w}</div>'


def ex(title, steps, answer=None):
    body = ''
    for s in steps:
        if isinstance(s, tuple) and s[0] == 'calc':
            body += f'<div class="calc">{s[1]}</div>'
        else:
            body += f'<div class="step">{s}</div>'
    ans = f'<div class="ans">پاسخ نهایی: {answer}</div>' if answer else ''
    return f'<div class="ex"><div class="title">{title}</div>{body}{ans}</div>'


def h2(title, mark):
    return f'<h2>{title} <span class="mark">[{mark}]</span></h2>'


def make_index(pg, total):
    def row(kw, sec, tip, key):
        return (f'<tr><td>{kw}</td><td>{sec}</td><td>{tip}</td>'
                f'<td><b>{pg.get(key, "?")}</b></td></tr>')
    return f'''
{h2("فهرست صفحات (شماره واقعی همین PDF)", "INDEX")}
<div class="note">در امتحان برو به <b>شماره صفحه</b> ستون آخر. این شماره‌ها با پاصفحه PDF یکی هستند.</div>
<table>
<tr><th>کلمه کلیدی سوال</th><th>بخش</th><th>چه بنویسی</th><th>صفحه</th></tr>
{row("چیت‌شیت و فرمول‌های حیاتی", "چیت‌شیت", "تعریف + فرمول", "CHEAT")}
{row("TF-IDF / Collaborative Filtering", "بخش 1", "فرمول + مثال عددی", "S1")}
{row("Cluster ↔ RDBMS / Hadoop", "بخش 2", "جدول تفاوت‌ها", "S2")}
{row("MapReduce / Combiner / Pregel", "بخش 3", "۳ مرحله + خرابی", "S3")}
{row("Join / جبر رابطه‌ای", "بخش 4", "مثال Join", "S4")}
{row("Matrix × Vector", "بخش 5", "Map/Reduce + عدد", "S5")}
{row("Shingle / Jaccard / MinHash / LSH / PCY", "بخش 6", "تعریف + فرمول + مثال", "S6")}
{row("فاصله‌ها / اسمی / دودویی", "بخش 7", "فرمول + مثال", "S7")}
{row("Apriori / Closed / Maximal", "بخش 8", "Passها + M⊆C⊆F", "S8")}
{row("Clustering / K-Means / DBSCAN / BFR", "بخش 9", "مثال یک تکرار", "S9")}
{row("حفظیات کامل KDD / مخازن / Hadoop", "تکمله A", "تعریف‌های جزئی", "D1")}
{row("اجرای داخلی / هزینه / Multi-way Join", "تکمله B", "جزئیات MapReduce", "D2")}
{row("MinHash / LSH / CHARM با جزئیات", "تکمله C", "اثبات و دام‌ها", "D3")}
{row("الگوریتم‌های خوشه‌بندی کامل", "تکمله D", "فرض/مراحل/مقایسه", "D4")}
{row("<b>حل نمونه سوالات استاد</b>", "<b>بخش 10</b>", "<b>پاسخ آماده</b>", "S10")}
</table>
<p class="small">کل صفحات PDF: <b>{total}</b> &nbsp;|&nbsp;
چیت‌شیت → ص{pg.get("CHEAT")} &nbsp;|&nbsp;
بخش1→ص{pg.get("S1")} · بخش2→ص{pg.get("S2")} · بخش3→ص{pg.get("S3")} · بخش4→ص{pg.get("S4")} · بخش5→ص{pg.get("S5")} ·
بخش6→ص{pg.get("S6")} · بخش7→ص{pg.get("S7")} · بخش8→ص{pg.get("S8")} · بخش9→ص{pg.get("S9")} · بخش10→ص{pg.get("S10")}</p>
'''


title = '''
<h1>جزوه امتحانی — داده‌های حجیم (Big Data Analytics)</h1>
<div class="meta">
<b>استاد:</b> دکتر فرساد زمانی بروجنی &nbsp;|&nbsp;
<b>امتحان:</b> جزوه‌باز — ۹۰ دقیقه &nbsp;|&nbsp;
<b>منبع:</b> لکچرهای ترم + نمونه سوالات + MMDS
</div>
<div class="note">
<b>روش پاسخ:</b> تعریف یک‌خطی ← فرمول داخل باکس ← مثال عددی کوتاه.
اول <b>فهرست صفحات</b> و <b>چیت‌شیت</b> را ببین. اگر سوال شبیه نمونه استاد بود → بخش 10.
</div>
'''

cheat = h2('چیت‌شیت سریع', 'CHEAT') + '''
<table>
<tr><th>مفهوم</th><th>تعریف یک‌خطی (همین را بنویس)</th></tr>
<tr><td><b>Shingle</b></td><td>دنباله k حرف/کلمه پشت‌سرهم در سند</td></tr>
<tr><td><b>Jaccard</b></td><td>اندازه اشتراک دو مجموعه ÷ اندازه اجتماع</td></tr>
<tr><td><b>MinHash</b></td><td>احتمال برابر شدن hash دو مجموعه = Jaccard</td></tr>
<tr><td><b>LSH</b></td><td>فقط جفت‌های احتمالاً مشابه را candidate می‌کند</td></tr>
<tr><td><b>Collaborative Filtering</b></td><td>توصیه بر اساس کاربران یا آیتم‌های شبیه</td></tr>
<tr><td><b>Closed itemset</b></td><td>پرتکرار؛ هیچ ابرمجموعه‌ای با همان support ندارد</td></tr>
<tr><td><b>Maximal itemset</b></td><td>پرتکرار؛ هیچ ابرمجموعه پرتکراری ندارد</td></tr>
<tr><td><b>MapReduce</b></td><td>پردازش موازی با Map و Reduce + تحمل خرابی</td></tr>
</table>
''' + eq(
    ['TFᵢⱼ  =  fᵢⱼ  /  maxₖ(fₖⱼ)',
     'IDFᵢ   =  log₂(N / nᵢ)',
     'TF-IDF = TFᵢⱼ × IDFᵢ'],
    ['fᵢⱼ = تعداد تکرار کلمه i در سند j',
     'maxₖ(fₖⱼ) = بیشترین تکرار هر کلمه در همان سند j',
     'N = تعداد کل اسناد',
     'nᵢ = تعداد اسنادی که کلمه i در آن‌ها آمده']
) + eq(
    ['J(A, B) = |A ∩ B| / |A ∪ B|',
     'Pr[ hπ(C₁) = hπ(C₂) ] = J(C₁, C₂)',
     'P(candidate) = 1 − (1 − sʳ)ᵇ']
) + eq(
    ['L₂ = √ Σ (xᵢ − yᵢ)²          L₁ = Σ |xᵢ − yᵢ|',
     'L∞ = max |xᵢ − yᵢ|           اسمی: d = (p − m) / p',
     'support(A⇒B) = support(A ∪ B)',
     'confidence(A⇒B) = support(A ∪ B) / support(A)',
     'M ⊆ C ⊆ F']
) + eq(
    ['Map: (i , mᵢⱼ × vⱼ)     Reduce: uᵢ = Σⱼ (mᵢⱼ × vⱼ)']
) + '''
<table>
<tr><th>مقایسه</th><th>نکته طلایی</th></tr>
<tr><td>RDBMS ↔ Cluster</td><td>عمودی/ACID ↔ افقی/commodity و انتقال کد به داده</td></tr>
<tr><td>K-Means ↔ K-Medoids</td><td>میانگین (حساس به پرت) ↔ نقطه واقعی داده</td></tr>
<tr><td>Combiner</td><td>فقط اگر Reduce انجمنی و جابجایی‌پذیر باشد</td></tr>
</table>
'''

s1 = h2('بخش 1 — مقدمه Big Data و TF-IDF', 'S1') + '''
<h3>سه V</h3>
<ul>
<li><b>Volume:</b> حجم خیلی زیاد</li>
<li><b>Velocity:</b> تولید با سرعت بالا</li>
<li><b>Variety:</b> شکل‌های مختلف داده</li>
</ul>
<p><b>داده‌کاوی:</b> استخراج الگو/دانش مفید از داده.</p>
<p><b>دو تکنیک:</b> خلاصه‌سازی (PageRank، خوشه‌بندی) و استخراج ویژگی (مشابهت، frequent itemsets، توصیه‌گر).</p>
<p><b>PageRank:</b> صفحه مهم است اگر از صفحات مهم لینک بگیرد.</p>
<p><b>اصل Bonferroni:</b> در داده عظیم، رخداد خیلی نادر هم زیاد دیده می‌شود → خطر False Positive.</p>
<p><b>Hash:</b> h(x) = x mod B &nbsp;|&nbsp; <b>Index:</b> بازیابی سریع رکورد &nbsp;|&nbsp; <b>دیسک:</b> خیلی کندتر از RAM؛ الگوریتم باید I/O کم کند.</p>
<h3>TF-IDF به زبان ساده</h3>
<p>کلمه مفید = در <b>تعداد کمی سند</b>، <b>زیاد</b> تکرار شده. کلماتی مثل «و» یا the که همه جا هستند، مفید نیستند (stop words).</p>
''' + eq(
    ['TFᵢⱼ = fᵢⱼ / maxₖ(fₖⱼ)',
     'IDFᵢ = log₂(N / nᵢ)',
     'TF-IDF = TFᵢⱼ × IDFᵢ']
) + ex('مثال 1 — دقیقاً مثل سوال استاد (قدم‌به‌قدم)', [
    'فرض: تعداد کل اسناد N = 1024',
    'کلمه w در 128 سند آمده (n = 128)',
    'در سند j این کلمه 10 بار آمده',
    'پرتکرارترین کلمه همان سند 100 بار آمده',
    ('calc',
     'گام 1) TF = 10 / 100 = 0.1\n'
     'گام 2) IDF = log2(1024 / 128) = log2(8) = 3\n'
     '         چون 2^3 = 8\n'
     'گام 3) TF-IDF = 0.1 × 3 = 0.3'),
], '0.3') + ex('مثال 2 — برای فهم بهتر', [
    'اگر کلمه‌ای در همه سندها باشد: IDF = log2(1) = 0 → بی‌اهمیت.',
    'کلمه «هادوپ» فقط در 1 سند از 3 سند آمده، 8 بار؛ max همان سند = 20:',
    ('calc', 'TF = 8/20 = 0.4\nIDF = log2(3/1) ≈ 1.58\nTF-IDF ≈ 0.4 × 1.58 = 0.63'),
], '≈ 0.63') + '''
<h3>Collaborative Filtering</h3>
<ul>
<li><b>User-based:</b> کاربران شبیه تو چه چیزهایی را پسندیده‌اند؟ همان‌ها را به تو پیشنهاد بده.</li>
<li><b>Item-based:</b> آیتم‌های شبیه آنچه پسندیده‌ای را پیشنهاد بده.</li>
</ul>
<p class="small">در درس به Recommendation Engine (مثل Netflix و Amazon) و Behavioral Data اشاره شده.</p>
'''

s2 = h2('بخش 2 — Cluster Computing در برابر RDBMS و Hadoop', 'S2') + '''
<p><b>محدودیت‌های RDBMS:</b> مقیاس‌پذیری گران، سرعت، تحمل خرابی، پردازش پیشرفته روی ترابایت/پتابایت.</p>
<p><b>ویژگی‌های Cluster (حفظ کن):</b> High Availability، Fault Tolerance، Data Replication، Load Balancing، Automated Failover، Backup & Recovery، Monitoring، Scalability افقی.</p>
<table>
<tr><th>موضوع</th><th>RDBMS سنتی</th><th>Cluster / Hadoop</th></tr>
<tr><td>سخت‌افزار</td><td>سرور گران</td><td>commodity ارزان</td></tr>
<tr><td>مقیاس</td><td>عمودی (تقویت یک سرور)</td><td>افقی (افزودن نود)</td></tr>
<tr><td>تحمل خرابی</td><td>غالباً سخت‌افزاری</td><td>نرم‌افزاری با replication</td></tr>
<tr><td>ایده پردازش</td><td>داده را پیش کد ببر</td><td><b>کد را پیش داده ببر</b></td></tr>
</table>
''' + ex('نمونه پاسخ آماده برای امتحان', [
    '۱) RDBMS برای داده ساخت‌یافته و تراکنش ACID عالی است، ولی وقتی داده خیلی بزرگ شود هزینه و سرعت مشکل می‌شود.',
    '۲) Cluster Computing با سرورهای ارزان، کپی داده و failover خودکار، مقیاس افقی می‌دهد.',
    '۳) جمله طلایی: در Hadoop به‌جای کشیدن همه داده به یک ماشین، برنامه را به جایی می‌فرستیم که داده هست.',
]) + '''
<p><b>Hadoop:</b> Scalable + Fault Tolerant &nbsp;|&nbsp; HDFS + MapReduce &nbsp;|&nbsp;
NameNode / DataNode / JobTracker / TaskTracker &nbsp;|&nbsp; معمولاً هر chunk سه کپی دارد.</p>
<p><b>SQL در برابر NoSQL:</b> SQL اسکیمای ثابت و ACID؛ NoSQL اسکیما انعطاف‌پذیر و مقیاس افقی.</p>
'''

s3 = h2('بخش 3 — MapReduce', 'S3') + '''
<p>تو فقط دو تابع می‌نویسی؛ سیستم بقیه کار را می‌کند.</p>
<ol>
<li><b>Map:</b> هر تکه ورودی را بخوان و جفت‌های (کلید، مقدار) بساز.</li>
<li><b>Shuffle:</b> همه مقدارهایی که کلید یکسان دارند را در یک لیست بگذار.</li>
<li><b>Reduce:</b> برای هر کلید، لیست مقدارها را ترکیب کن (جمع، شمارش، ...).</li>
</ol>
''' + eq(
    ['Map:     input  →  (key, value)',
     'Shuffle: (k,v1), (k,v2), ...  →  (k, [v1, v2, ...])',
     'Reduce:  (k, [v1, v2, ...])  →  (k, result)']
) + ex('مثال خیلی ساده — شمارش کلمه', [
    'دو جمله داریم: «big data» و «big data systems»',
    ('calc',
     'Map از جمله 1:  (big,1)  (data,1)\n'
     'Map از جمله 2:  (big,1)  (data,1)  (systems,1)\n\n'
     'بعد از Shuffle:\n'
     '  big → [1, 1]\n'
     '  data → [1, 1]\n'
     '  systems → [1]\n\n'
     'Reduce (جمع):\n'
     '  big = 2\n'
     '  data = 2\n'
     '  systems = 1'),
], 'big=2 ، data=2 ، systems=1') + '''
<p><b>Combiner:</b> اگر عمل Reduce جابجایی‌پذیر و انجمنی باشد (مثل جمع)، می‌توان قبل از شبکه یک Reduce محلی زد تا ترافیک کم شود.</p>
<table>
<tr><th>اگر این خراب شود</th><th>چه کار می‌کنند؟</th></tr>
<tr><td>Master</td><td>معمولاً کل Job از نو شروع می‌شود</td></tr>
<tr><td>Map Worker</td><td>همان Mapها روی نود سالم دوباره اجرا می‌شوند</td></tr>
<tr><td>Reduce Worker</td><td>Reduce دوباره اجرا می‌شود</td></tr>
</table>
<p><b>Workflow Systems:</b> به‌جای فقط Map→Reduce، یک گراف DAG از توابع (Clustera، Hyracks).</p>
<p><b>Pregel:</b> سیستم محاسبات گرافی با SuperStep و Checkpoint برای تحمل خرابی در الگوریتم‌های بازگشتی.</p>
<p><b>PageRank تکراری:</b></p>
''' + eq(['v⁽ᵗ⁺¹⁾ = M × v⁽ᵗ⁾   تا وقتی تغییر خیلی کم شود'])

s4 = h2('بخش 4 — جبر رابطه‌ای با MapReduce', 'S4') + '''
<table>
<tr><th>عملیات</th><th>ایده ساده</th></tr>
<tr><td>Selection</td><td>فقط تاپل‌هایی که شرط دارند را نگه دار</td></tr>
<tr><td>Projection</td><td>بعضی ستون‌ها را بردار؛ تکراری‌ها را در Reduce حذف کن</td></tr>
<tr><td>Union</td><td>همه را بفرست؛ تکراری یکی شود</td></tr>
<tr><td>Intersection</td><td>فقط چیزی که در هر دو آمده</td></tr>
<tr><td>Difference R−S</td><td>چیزی که فقط در R است</td></tr>
<tr><td>Join</td><td>کلید = ستون مشترک؛ دو طرف را به هم بچسبان</td></tr>
<tr><td>Group + Aggregation</td><td>کلید = گروه؛ Reduce = SUM/COUNT/AVG</td></tr>
</table>
''' + ex('مثال Join برای مبتدی', [
    'جدول R: (علی، تهران) و (مینا، اصفهان)',
    'جدول S: (تهران، ایران) و (اصفهان، ایران)',
    'می‌خواهیم روی «شهر» Join کنیم:',
    ('calc',
     'Map: کلید = شهر\n'
     '  تهران → از R: علی   و از S: ایران\n'
     '  اصفهان → از R: مینا و از S: ایران\n\n'
     'Reduce تهران:  (علی، تهران، ایران)\n'
     'Reduce اصفهان: (مینا، اصفهان، ایران)'),
], '(علی،تهران،ایران) و (مینا،اصفهان،ایران)') + '''
<p><b>Multi-way Join:</b> Join همزمان چند جدول. هزینه انتقال داده مهم است؛ Replication Rate نشان می‌دهد هر ورودی چند بار کپی می‌شود.</p>
'''

s5 = h2('بخش 5 — ضرب ماتریس با MapReduce', 'S5') + '''
<p>هدف ماتریس×بردار: برای هر سطر ماتریس یک عدد بساز = ضرب داخلی آن سطر در بردار.</p>
''' + eq(
    ['uᵢ = mᵢ₁·v₁ + mᵢ₂·v₂ + … + mᵢₙ·vₙ',
     'Map:    (i , mᵢⱼ × vⱼ)',
     'Reduce: برای هر i همه مقدارها را جمع کن']
) + ex('مثال کامل — انگار اولین بار می‌بینی', [
    'ماتریس و بردار:',
    ('calc',
     'M =  1  0  5      V =  2\n'
     '     7  3  0           4\n'
     '     1  3  5           6'),
    '<b>گام Map:</b> هر خانه ماتریس را در عنصر متناظر بردار ضرب کن. کلید = شماره سطر.',
    ('calc',
     'سطر 1: (1, 1×2=2) ، (1, 0×4=0) ، (1, 5×6=30)\n'
     'سطر 2: (2, 7×2=14)، (2, 3×4=12)، (2, 0×6=0)\n'
     'سطر 3: (3, 1×2=2) ، (3, 3×4=12)، (3, 5×6=30)'),
    '<b>گام Shuffle:</b> مقدارهای هر سطر را کنار هم بگذار.',
    ('calc',
     'کلید 1 → [2, 0, 30]\n'
     'کلید 2 → [14, 12, 0]\n'
     'کلید 3 → [2, 12, 30]'),
    '<b>گام Reduce:</b> جمع کن.',
    ('calc',
     'u1 = 2+0+30 = 32\n'
     'u2 = 14+12+0 = 26\n'
     'u3 = 2+12+30 = 44'),
], 'U = [32, 26, 44]') + '''
<h3>ماتریس × ماتریس (دو Job)</h3>
''' + eq(['pᵢₖ = Σⱼ (mᵢⱼ × nⱼₖ)']) + '''
<p>Job1: روی j جوین کن و ضرب‌های جزئی بساز. Job2: برای هر (i,k) جمع بزن.</p>
''' + ex('چک یک خانه', [
    ('calc', 'خانه (1,1) از P: 1×2 + 0×4 + 5×6 = 2+0+30 = 32'),
])

s6 = h2('بخش 6 — Shingle ، MinHash ، LSH', 'S6') + eq(
    ['Document → Shingles → MinHash Signature → LSH → Candidates → Exact check']
) + '''
<h3>Shingle چیست؟</h3>
<p>یک پنجره به طول k روی متن می‌گذاری و هر بار یک تکه برمی‌داری.</p>
''' + ex('مثال', [
    'متن: abcab و k = 2',
    ('calc', 'تکه‌ها: ab ، bc ، ca ، ab\nمجموعه بدون تکرار: {ab, bc, ca}'),
]) + '''
<h3>Jaccard</h3>
''' + eq(['J(A,B) = |A ∩ B| / |A ∪ B|']) + ex('مثال با میوه', [
    'A = {سیب، پرتقال، موز} و B = {موز، انگور}',
    ('calc',
     'اشتراک = {موز}                 → 1\n'
     'اجتماع  = {سیب،پرتقال،موز،انگور} → 4\n'
     'J = 1/4 = 0.25\n'
     'فاصله = 1 - 0.25 = 0.75'),
], 'J = 0.25') + '''
<h3>MinHash</h3>
<p>عناصر را تصادفی مرتب کن. برای هر مجموعه، <b>اولین</b> عنصری که در آن ترتیب می‌بینی را به‌عنوان hash بردار.</p>
''' + eq(['Pr[ هش دو مجموعه برابر شود ] = Jaccard همان دو مجموعه']) + ex('مثال', [
    'A = {1,3,4} و B = {2,3,4,5}',
    ('calc', 'Jaccard واقعی = 2/5 = 0.4'),
    'یک ترتیب تصادفی فرضی: 3 ، 1 ، 5 ، 2 ، 4',
    ('calc',
     'اولین عنصر A در این ترتیب = 3\n'
     'اولین عنصر B در این ترتیب = 3\n'
     'پس hashها برابر شدند'),
    'اگر خیلی ترتیب تصادفی بگیری، نسبت دفعاتی که برابر می‌شوند حدود 0.4 می‌شود.',
]) + '''
<h3>LSH</h3>
<p>امضا را به چند نوار (band) تقسیم کن. اگر دو سند حتی در <b>یک نوار</b> کاملاً یکسان بودند، آن‌ها را candidate حساب کن و بعد دقیق چک کن.</p>
''' + eq(
    ['P = 1 − (1 − sʳ)ᵇ'],
    ['s = شباهت واقعی', 'r = تعداد سطر در هر band', 'b = تعداد bandها']
) + ex('مثال عددی', [
    'b = 20 ، r = 5 ، s = 0.8',
    ('calc',
     's^r = 0.8^5 ≈ 0.328\n'
     '(1 - 0.328)^20 = 0.672^20 ≈ 0.00035\n'
     'P = 1 - 0.00035 ≈ 0.99965'),
    'یعنی حدود 99.97٪ احتمال دارد جفت واقعاً مشابه را پیدا کنیم.',
], 'P ≈ 0.99965') + '''
<p><b>PCY:</b> در گذر اول علاوه بر شمارش اقلام، جفت‌ها را به bucket هش کن. در گذر دوم فقط جفتی را بشمار که هر دو قلم frequent باشند و bucketشان هم frequent باشد.</p>
'''

s7 = h2('بخش 7 — فاصله‌ها و تشابه تاپل‌ها', 'S7') + '''
<p><b>چهار شرط Metric:</b> نامنفی، صفر فقط وقتی دو شیء یکی باشند، تقارن، نامساوی مثلثی.</p>
''' + eq(
    ['L₂ (اقلیدسی) = √( (x₁−y₁)² + (x₂−y₂)² + … )',
     'L₁ (منهتن)   = |x₁−y₁| + |x₂−y₂| + …',
     'L∞           = بزرگ‌ترین |xᵢ − yᵢ|']
) + ex('مثال روی یک جفت نقطه', [
    'X = (1, 2) و Y = (4, 6)',
    ('calc',
     'L2 = √( (1-4)² + (2-6)² ) = √(9+16) = √25 = 5\n'
     'L1 = |1-4| + |2-6| = 3 + 4 = 7\n'
     'L∞ = max(3, 4) = 4'),
]) + eq(
    ['برای صفات اسمی:  d = (p − m) / p'],
    ['p = تعداد کل صفات', 'm = تعداد صفاتی که مقدارشان یکی است']
) + ex('مثال اسمی', [
    'شخص1: (مرد، تهران، لیسانس)',
    'شخص2: (زن، تهران، لیسانس)',
    ('calc', 'p = 3\nm = 2   (شهر و مدرک یکسان‌اند)\nd = (3-2)/3 = 1/3 ≈ 0.33'),
], '1/3') + '''
<p><b>دودویی:</b> q = هر دو 1 &nbsp;|&nbsp; r = (0,1) &nbsp;|&nbsp; s = (1,0) &nbsp;|&nbsp; t = هر دو 0</p>
''' + eq(
    ['متقارن:   d = (r + s) / (q + r + s + t)',
     'نامتقارن: d = (r + s) / (q + r + s)     ← صفر-صفر مهم نیست',
     'Jaccard:  J = q / (q + r + s)']
) + '''
<p><b>Cosine</b> برای متن خوب است. <b>Hamming</b> = تعداد خانه‌های متفاوت. <b>Edit distance</b> = |X| + |Y| − 2×|LCS|.</p>
<p><b>Data Matrix:</b> سطر = تاپل، ستون = صفت. <b>Dissimilarity Matrix:</b> فاصله بین تاپل‌ها؛ قطر اصلی صفر.</p>
'''

s8 = h2('بخش 8 — Apriori ، Closed ، Maximal', 'S8') + eq(
    ['support(X) = (تعداد تراکنش شامل X) / (کل تراکنش‌ها)',
     'support(A ⇒ B) = support(A ∪ B)',
     'confidence(A ⇒ B) = support(A ∪ B) / support(A)',
     'M ⊆ C ⊆ F']
) + ex('مثال قانون انجمنی', [
    'از 100 سبد خرید: نان در 40 سبد، نان+شیر در 30 سبد.',
    ('calc',
     'قانون: نان ⇒ شیر\n'
     'support = 30/100 = 0.3\n'
     'confidence = 30/40 = 0.75 = 75%'),
    'یعنی 75٪ کسانی که نان گرفته‌اند شیر هم گرفته‌اند.',
], 'conf = 75%') + '''
<table>
<tr><th>نوع</th><th>معنی ساده</th></tr>
<tr><td>Closed</td><td>اگر قلمی اضافه کنی، support دیگر همان عدد قبلی نمی‌ماند</td></tr>
<tr><td>Maximal</td><td>اگر قلمی اضافه کنی، دیگر frequent نیست</td></tr>
</table>
''' + ex('مثال Closed و Maximal', [
    'تراکنش‌ها: {A,B,C} ، {A,B} ، {A,B,C} ، {A,C} و حداقل شمارش = 2',
    ('calc',
     'A=4 ، B=3 ، C=3\n'
     'AB=3 ، AC=3 ، BC=2\n'
     'ABC=2\n\n'
     'Closedها: A ، AB ، AC ، ABC\n'
     '(B closed نیست چون AB همان support=3 را دارد)\n\n'
     'Maximal فقط: ABC'),
]) + '''
<p><b>اصل Apriori:</b> اگر مجموعه‌ای frequent باشد، همه زیرمجموعه‌هایش هم frequentاند. پس کاندید بزرگ را فقط از frequentهای کوچک می‌سازیم.</p>
<p><b>CHARM:</b> الگوریتم استخراج Closed با اشتراک tidsetها.</p>
'''

s9 = h2('بخش 9 — خوشه‌بندی', 'S9') + '''
<p><b>هدف:</b> اعضای یک خوشه به هم نزدیک؛ خوشه‌های مختلف از هم دور. یادگیری بدون سرپرست (برخلاف طبقه‌بندی).</p>
<p>انواع: Partitioning (K-Means، K-Medoids، PAM، CLARA، CLARANS) · Hierarchical (AGNES، DIANA) ·
Density (DBSCAN، OPTICS، DENCLUE) · Grid (STING، CLIQUE)</p>
''' + ex('مثال K-Means — فقط یک تکرار', [
    'نقاط: A(1,1) ، B(1,2) ، C(4,4) ، D(5,4)',
    'مراکز اولیه: μ1 = A(1,1) و μ2 = C(4,4)',
    '<b>تخصیص:</b> هر نقطه به نزدیک‌ترین مرکز می‌رود.',
    ('calc',
     'A و B نزدیک μ1 هستند → C1 = {A, B}\n'
     'C و D نزدیک μ2 هستند → C2 = {C, D}'),
    '<b>به‌روزرسانی مرکز:</b> میانگین بگیر.',
    ('calc',
     'μ1 = ( (1+1)/2 , (1+2)/2 ) = (1 , 1.5)\n'
     'μ2 = ( (4+5)/2 , (4+4)/2 ) = (4.5 , 4)'),
], 'مراکز جدید: (1, 1.5) و (4.5, 4)') + '''
<p><b>Linkage:</b> Single = کمینه فاصله بین دو خوشه · Complete = بیشینه · Average = میانگین · Centroid = فاصله مراکز.</p>
<p><b>K-Medoids / PAM:</b> نماینده خوشه یک نقطه واقعی است (مقاوم‌تر به پرت). CLARA روی نمونه کار می‌کند؛ CLARANS جستجوی تصادفی می‌کند.</p>
''' + eq(
    ['DBSCAN: اگر در شعاع Eps حداقل MinPts نقطه باشد → Core Point',
     'Border = کنار Core است ولی خودش Core نیست',
     'Noise = هیچ‌کدام']
) + eq(
    ['BFR (داده بزرگ اقلیدسی):',
     'centroidᵢ = SUMᵢ / N',
     'varianceᵢ = SUMSQᵢ/N − (SUMᵢ/N)²']
) + '''
<p><b>CURE:</b> چند نقطه نماینده برای خوشه‌های غیرکروی. <b>OPTICS:</b> وقتی چگالی خوشه‌ها فرق می‌کند، بهتر از DBSCAN است.</p>
'''

s10 = h2('بخش 10 — حل کامل نمونه سوالات استاد', 'S10') + '''
<div class="note">امتحان نمونه: ۹۰ دقیقه — ۱۰ نمره توصیفی</div>
<h3>سوال 1 — تعاریف</h3>
<p><b>الف) Min-hashing:</b> از مجموعه بزرگ امضای کوتاه می‌سازیم طوری که احتمال برابر شدن hash دو مجموعه برابر Jaccard باشد.</p>
''' + eq(['Pr[ h(C₁) = h(C₂) ] = J(C₁, C₂)']) + '''
<p><b>ب) Collaborative Filtering:</b> توصیه‌گر مبتنی بر شباهت کاربران یا آیتم‌ها (مثل Netflix/Amazon).</p>
<p><b>ج) Jaccard:</b></p>
''' + eq(['J(A,B) = |A ∩ B| / |A ∪ B|']) + '''
<p><b>د) Shingle:</b> دنباله k توکن متوالی در سند.</p>
<h3>سوال 2 — Cluster در برابر RDBMS</h3>
<p>RDBMS: مقیاس غالباً عمودی، ACID، داده ساخت‌یافته، در حجم خیلی بالا گران/کند.<br>
Cluster: مقیاس افقی، commodity servers، replication و failover، انتقال کد به سمت داده.</p>
<h3>سوال 3 — Matrix×Vector با MapReduce</h3>
''' + eq(
    ['Map: (i , mᵢⱼ × vⱼ)',
     'Reduce: uᵢ = مجموع همه مقدارهای کلید i']
) + '''
<p>مثال عددی کامل در بخش 5.</p>
<h3>سوال 4 — TF-IDF</h3>
''' + ex('حل سوال استاد', [
    ('calc',
     'TF = 10/100 = 0.1\n'
     'IDF = log2(1024/128) = log2(8) = 3\n'
     'TF-IDF = 0.1 × 3 = 0.3'),
], '0.3') + '''
<h3>سوال 5 — Apriori با MST = 0.3</h3>
<table>
<tr><th>TID</th><th>اقلام</th><th>TID</th><th>اقلام</th></tr>
<tr><td>1</td><td>a, b</td><td>5</td><td>a, b, c</td></tr>
<tr><td>2</td><td>b, c</td><td>6</td><td>d, f</td></tr>
<tr><td>3</td><td>a, b, c</td><td>7</td><td>c, d, e, f</td></tr>
<tr><td>4</td><td>d, e, f</td><td>8</td><td>a, b, c, d, e</td></tr>
</table>
''' + ex('حل قدم‌به‌قدم', [
    'تعداد تراکنش = 8 و minsup = 0.3 → حداقل شمارش باید ≥ 3 باشد (چون 2/8 = 0.25 از 0.3 کمتر است).',
    '<b>Pass 1:</b>',
    ('calc', 'a=4, b=5, c=5, d=4, e=3, f=3\nهمه ≥ 3 → L1 = {a,b,c,d,e,f}'),
    '<b>Pass 2:</b>',
    ('calc',
     'ab=4 ✓  ac=3 ✓  bc=4 ✓\n'
     'de=3 ✓  df=3 ✓\n'
     'cd=2 ✗  ce=2 ✗  ef=2 ✗\n'
     'L2 = {ab, ac, bc, de, df}'),
    '<b>Pass 3:</b> فقط abc قابل ساخت است (ab و ac و bc همه frequentاند). def نه، چون ef frequent نیست.',
    ('calc', 'abc در تراکنش‌های 3 و 5 و 8 → count=3 ✓\nL3 = {abc}'),
    'Pass 4 کاندیدی ندارد → توقف.',
], 'L2={ab,ac,bc,de,df} و L3={abc}') + '''
<hr>
<div class="note"><b>چک‌لیست ۳۰ ثانیه‌ای:</b> تعریف یک‌خطی؟ فرمول؟ مثال عددی؟ تفاوت با مفهوم نزدیک؟</div>
<p class="small">
موارد اضافه‌شده پس از مرور لکچرها: Hash/Index/دیسک، Bonferroni، Pregel، Multi-way Join، PCY، OPTICS/CURE/BFR.
Data Streams و Online Advertising فقط در فهرست کلی overview بودند و اسلاید کامل در فایل‌های ارسالی نبود؛ تمرکز نمونه سوالات استاد روی Similar Items، MapReduce، TF-IDF، Cluster/RDBMS و Apriori است.
</p>
'''

# جزئیات تکمیلی مستقیماً از لکچرها؛ برای پاسخ‌های تشریحی و حفظی
d1 = h2('تکمله A — حفظیات داده‌کاوی، KDD، مخازن داده و Hadoop', 'D1') + '''
<h3>داده‌کاوی در برابر KDD</h3>
<p><b>داده‌کاوی</b> استخراج دانش از حجم زیاد داده است؛ نام‌های نزدیک آن: استخراج دانش،
تحلیل داده/الگو، باستان‌شناسی داده، لای‌روبی داده و KDD. بااین‌حال در تعریف فرایندی،
داده‌کاوی فقط <b>یک مرحله</b> از KDD است.</p>
<ol>
<li><b>Data Cleaning:</b> حذف نویز، تناقض و داده غلط</li>
<li><b>Data Integration:</b> ترکیب چند منبع</li>
<li><b>Data Selection:</b> انتخاب داده مرتبط با مسئله</li>
<li><b>Data Transformation:</b> تبدیل، تجمیع و نرمال‌سازی</li>
<li><b>Data Mining:</b> اجرای روش استخراج الگو</li>
<li><b>Pattern Evaluation:</b> تشخیص الگوهای معتبر و جالب</li>
<li><b>Knowledge Presentation:</b> نمایش و مصورسازی دانش</li>
</ol>

<h3>وظایف داده‌کاوی: حفظیات مهم</h3>
<table>
<tr><th>وظیفه</th><th>تعریف</th><th>مثال</th></tr>
<tr><td>Descriptive</td><td>توصیف ساختار و روابط موجود</td><td>خوشه‌بندی، قوانین انجمنی</td></tr>
<tr><td>Predictive</td><td>پیش‌بینی کلاس یا مقدار ناشناخته</td><td>طبقه‌بندی، رگرسیون</td></tr>
<tr><td>Characterization</td><td>خلاصه ویژگی‌های یک کلاس هدف</td><td>ویژگی مشتریان وفادار</td></tr>
<tr><td>Discrimination</td><td>مقایسه کلاس هدف با کلاس متضاد</td><td>وفادار در برابر ریزشی</td></tr>
<tr><td>Outlier Analysis</td><td>کشف شیء ناسازگار با الگوی عمومی</td><td>تقلب کارت اعتباری</td></tr>
<tr><td>Evolution Analysis</td><td>مدل‌کردن روند تغییر در زمان</td><td>سری زمانی و الگوی دوره‌ای</td></tr>
</table>

<p><b>طبقه‌بندی:</b> یادگیری با برچسب؛ مدل می‌تواند IF–THEN، درخت تصمیم، فرمول یا
شبکه عصبی باشد. روش‌های نام‌برده در لکچر: Naive Bayes، SVM و KNN.</p>
<p><b>خوشه‌بندی:</b> بدون برچسب؛ گروه‌های طبیعی را کشف می‌کند. هر خوشه بعداً می‌تواند
یک کلاس تلقی شود.</p>
<p><b>Outlier:</b> ممکن است نویز باشد، اما گاهی مهم‌ترین دانش داده است؛ نباید همیشه حذف شود.</p>

<h3>انواع الگوی پرتکرار</h3>
<ul>
<li><b>Frequent Itemset:</b> اقلامی که مکرراً باهم رخ می‌دهند؛ مثل شیر و نان</li>
<li><b>Frequent Subsequence:</b> دنباله عملیاتی که مکرراً با همان ترتیب رخ می‌دهد</li>
<li><b>Frequent Substructure:</b> زیرساختار پرتکرار مثل گراف یا درخت</li>
</ul>

<h3>چه الگویی «جالب» است؟</h3>
<p>قابل‌فهم، معتبر، بالقوه مفید، جدید و نمایش‌دهنده دانش باشد. معیارهای عینی مانند
Support و Confidence آستانه‌ای دارند که کاربر تعیین می‌کند.</p>

<h3>معماری سیستم داده‌کاوی</h3>
<ol>
<li>پایگاه/انبار داده/Web یا مخزن دیگر</li>
<li>سرور پایگاه یا انبار داده</li>
<li>پایگاه دانش (Knowledge Base)</li>
<li>موتور داده‌کاوی</li>
<li>ماژول ارزیابی الگو</li>
<li>واسط کاربر</li>
</ol>

<h3>انواع مخزن داده</h3>
<table>
<tr><th>مخزن</th><th>تعریف و نکته</th></tr>
<tr><td>Relational DB</td><td>جدول، سطر/تاپل، ستون/صفت و کلید یکتا</td></tr>
<tr><td>Data Warehouse</td><td>داده یکپارچه چند منبع؛ پاک‌سازی، تبدیل و بارگذاری؛ مدل چندبعدی</td></tr>
<tr><td>Data Cube</td><td>نمای چندبعدی؛ نمونه ابعاد: زمان، کالا، مکان</td></tr>
<tr><td>Transactional DB</td><td>هر رکورد یک TID و فهرست اقلام دارد</td></tr>
<tr><td>Temporal</td><td>دارای صفت زمانی</td></tr>
<tr><td>Sequence</td><td>رویدادهای مرتب، با یا بدون timestamp</td></tr>
<tr><td>Time-series</td><td>اندازه‌گیری تکراری یک مقدار در زمان</td></tr>
<tr><td>Spatial</td><td>GIS/CAD/تصویر؛ نمایش Raster یا Vector</td></tr>
<tr><td>Text / Multimedia</td><td>متن، تصویر، صدا و ویدئو</td></tr>
<tr><td>Heterogeneous / Legacy</td><td>ترکیب سامانه‌های مستقل، قدیمی و ناهمگون</td></tr>
<tr><td>Data Stream</td><td>بسیار بزرگ/نامتناهی، پویا، یک یا چند scan، پاسخ سریع و بلادرنگ</td></tr>
</table>

<h3>چالش‌های داده‌کاوی</h3>
<ul>
<li>استخراج تعاملی در سطوح مختلف انتزاع و استفاده از دانش پس‌زمینه</li>
<li>زبان پرس‌وجوی داده‌کاوی، نمایش و مصورسازی نتایج</li>
<li>داده ناقص، نویزی و تشخیص الگوهای باکیفیت</li>
<li>کارایی و مقیاس‌پذیری؛ الگوریتم موازی، توزیع‌شده و افزایشی</li>
<li>انواع داده پیچیده و پایگاه‌های ناهمگون</li>
</ul>
<p><b>سطوح اتصال Mining به DB/DW (فهرست حفظی):</b>
No Coupling، Loose Coupling، Semitight Coupling و Tight Coupling.</p>

<h3>Bonferroni — مثال حفظی هتل</h3>
''' + eq([
    'P(ملاقات یک جفت در یک روز) = (0.01 × 0.01) / 10⁵ = 10⁻⁹',
    'E(دو ملاقات تصادفی) ≈ C(10⁹,2) × C(1000,2) × 10⁻¹⁸ ≈ 250,000'
]) + '''
<p>نتیجه: حتی با داده کاملاً تصادفی، حدود ۲۵۰هزار جفت «مشکوک» پیدا می‌شود؛
پس در داده عظیم، نادر بودن به‌تنهایی دلیل معناداری نیست.</p>

<h3>Hash، Index و دیسک — جزئیات</h3>
<ul>
<li>تابع هش خوب کلیدها را تقریباً یکنواخت بین B باکت توزیع می‌کند.</li>
<li>برای h(x)=x mod B معمولاً B اول انتخاب می‌شود تا الگوهای ورودی توزیع را خراب نکنند.</li>
<li>برخورد هش یعنی چند کلید در یک باکت؛ پس بعد از یافتن باکت باید مقدار واقعی بررسی شود.</li>
<li>دیسک بلوکی است؛ بلوک کوچک‌ترین واحد انتقال دیسک↔RAM است.</li>
<li>خواندن بلوک حدود 10ms و تقریباً 10⁵ برابر خواندن کلمه از RAM کندتر است.</li>
</ul>

<h3>Hadoop — جزئیات حفظی</h3>
<ul>
<li><b>فلسفه:</b> commodity server ارزان + تحمل خرابی نرم‌افزاری + انتقال کد به داده</li>
<li><b>اکوسیستم:</b> HDFS، MapReduce، HBase، Hive و Pig</li>
<li><b>NameNode:</b> metadata و محل بلوک‌ها؛ <b>DataNode:</b> خود بلوک‌ها</li>
<li><b>JobTracker:</b> زمان‌بندی Job؛ <b>TaskTracker:</b> اجرای Map/Reduce (معماری Hadoop 1)</li>
<li><b>Standalone:</b> فایل محلی و یک JVM</li>
<li><b>Pseudo-distributed:</b> یک ماشین ولی daemonها/HDFS جدا</li>
<li><b>Fully distributed:</b> چند نود و replication</li>
<li><b>Cloud:</b> AWS/S3 و Azure HDInsight/Blob Storage</li>
<li><b>نامناسب:</b> پایگاه تراکنشی با update بسیار مکرر</li>
</ul>
<p><b>کاربردهای تجاری:</b> Risk Modeling، Customer Churn، Recommendation Engine و Ad Targeting.</p>
<p><b>JVM:</b> Java به bytecode کامپایل می‌شود؛ هر process جاوا JVM و حافظه مجزا دارد.
فایل class مستقل از سیستم‌عامل است ولی JVM پلتفرم‌وابسته است.</p>
'''

d2 = h2('تکمله B — اجرای داخلی و توسعه‌های MapReduce', 'D2') + '''
<h3>Map Task، Partitioning و Grouping</h3>
<ul>
<li>عنصر ورودی (تاپل/سند) نباید بین دو chunk نصف شود.</li>
<li>Map می‌تواند برای یک ورودی صفر، یک یا چند زوج و حتی چند کلید یکسان تولید کند.</li>
<li>اگر r کاهنده باشد، h(k) یکی از 0 تا r−1 را انتخاب می‌کند.</li>
<li>هر Map برای هر Reduce یک فایل محلی میانی دارد؛ بنابراین r فایل می‌سازد.</li>
<li>شرط اصلی: کلیدهای یکسان حتماً به یک Reduce بروند؛ کلیدهای متفاوت می‌توانند هم‌مقصد شوند.</li>
</ul>
''' + eq([
    'k₁ = k₂  ⇒  h(k₁) = h(k₂)',
    '(k,v₁),(k,v₂),…  ⇒  (k,[v₁,v₂,…])'
]) + '''
<p><b>Grouping سیستمی</b> را با GROUP BY رابطه‌ای اشتباه نکن: Grouping فقط مقادیر
هم‌کلید را کنار هم قرار می‌دهد؛ Aggregation عملی است که کاربر در Reduce می‌نویسد.</p>

<h3>Combiner — دام مهم امتحانی</h3>
''' + eq([
    '(a ∘ b) ∘ c = a ∘ (b ∘ c)     (Associative)',
    'a ∘ b = b ∘ a                  (Commutative)'
]) + '''
<p>Combiner جای Reduce نهایی را نمی‌گیرد؛ فقط تکراری‌ها/مقادیر همان Map را ترکیب می‌کند.
مثلاً در Projection تکراری‌های دو Map مختلف فقط در Reduce نهایی حذف می‌شوند.</p>

<h3>عملیات رابطه‌ای — الگوریتم دقیق</h3>
<table>
<tr><th>عملیات</th><th>Map</th><th>Reduce</th></tr>
<tr><td>Selection σ</td><td>اگر C(t): emit(t,t)</td><td>عبور؛ اغلب Map-only</td></tr>
<tr><td>Projection π</td><td>emit(t′,t′)</td><td>یک t′ برای حذف تکرار</td></tr>
<tr><td>Union</td><td>از R و S: emit(t,t)</td><td>یک بار t</td></tr>
<tr><td>Intersection</td><td>R: emit(t,R)، S: emit(t,S)</td><td>اگر هر دو برچسب بودند</td></tr>
<tr><td>Difference R−S</td><td>همراه برچسب منبع</td><td>فقط labels={R}</td></tr>
<tr><td>Join</td><td>کلید=همه صفات مشترک</td><td>حاصل‌ضرب دکارتی محلی دو طرف</td></tr>
<tr><td>Grouping/Agg</td><td>کلید=صفات گروه</td><td>SUM/COUNT/AVG/MIN/MAX</td></tr>
</table>
<p><b>تفاضل جابجایی‌پذیر نیست:</b> R−S با S−R فرق دارد. در Intersection حتماً نام
رابطه را بفرست؛ دو تکرار از یک رابطه به معنی حضور در هر دو رابطه نیست.</p>
<p><b>Join:</b> اگر برای یک کلید، ۲ تاپل R و ۳ تاپل S باشد، Reduce باید ۲×۳=۶ خروجی بسازد.</p>

<h3>Matrix×Vector وقتی بردار در RAM جا نمی‌شود</h3>
<p>ماتریس را به نوارهای عمودی و بردار را به قطعات افقی متناظر تقسیم کن؛ تعداد نوارها
طوری باشد که قطعه بردار و chunk ماتریس در حافظه یک نود جا شود. هر Map سهم جزئی
uᵢ را می‌سازد و Reduce سهم نوارهای مختلف را روی i جمع می‌کند.</p>

<h3>Matrix×Matrix: دو Job در برابر یک Job</h3>
<p><b>دو Job:</b> Job1 روی j جوین و ((i,k),mᵢⱼnⱼₖ) تولید می‌کند؛ Job2 روی (i,k) جمع می‌زند.</p>
<p><b>یک Job:</b> هر mᵢⱼ برای تمام kها و هر nⱼₖ برای تمام iها تکثیر می‌شود. Job کمتر،
ولی Replication و ترافیک بیشتر.</p>

<h3>بستار تعدی (Transitive Closure)</h3>
''' + eq([
    'P = E ∪ { (x,y) | ∃z : P(x,z) ∧ P(z,y) }'
]) + '''
<p>اگر مسیر (1,2) و (2,3) داشته باشیم، Join روی گره میانی 2 مسیر (1,3) را می‌سازد.
دو نوع Task: Join Task و Duplicate-Elimination Task. مسیر جدید پس از حذف تکراری به
Join Taskهای مربوط به دو سر مسیر فرستاده می‌شود؛ توقف وقتی مسیر جدیدی ساخته نشود.</p>

<h3>Pregel</h3>
<ul>
<li>اجرای همگام در مرحله‌های SuperStep</li>
<li>Checkpoint = کپی وضعیت همه Taskها</li>
<li>در خرابی، بازگشت به آخرین Checkpoint</li>
<li>زمان ترمیم باید خیلی کمتر از میانگین زمان بین دو خرابی باشد</li>
</ul>

<h3>Communication Cost، Reducer Size و Replication Rate</h3>
''' + eq([
    'Communication Cost = Σ |Input هر Task|',
    'ρ = (تعداد کل خروجی‌های Map) / (تعداد عناصر ورودی)'
]) + '''
<p><b>Reducer Size (q):</b> بیشترین تعداد مقدار مجاز برای یک Reduce. q کوچک‌تر →
Reduceهای بیشتر و موازی‌سازی بیشتر؛ اگر ورودی Reduce در RAM جا شود I/O کمتر می‌شود.</p>
<p><b>Trade-off:</b> یک Reduce هزینه انتقال حداقل ولی زمان اجرا زیاد؛ Reduceهای بیشتر
زمان کمتر ولی احتمال تکثیر/هزینه بیشتر.</p>

<h3>Multi-way Join یک‌مرحله‌ای</h3>
<p>برای R(A,B) ⋈ S(B,C) ⋈ T(C,D)، تعداد باکت B برابر b و C برابر c است؛ پس k=bc کاهنده.</p>
<ul>
<li>S(v,w) فقط به Reduce با آدرس (h(v),g(w)) می‌رود.</li>
<li>R(u,v) چون C ندارد به تمام c ستون تکثیر می‌شود.</li>
<li>T(w,x) چون B ندارد به تمام b سطر تکثیر می‌شود.</li>
</ul>
''' + eq([
    'CCᵣₑdᵤcₑ = s + c·r + b·t       با شرط b·c = k',
    'b* = √(k·r/t)       c* = √(k·t/r)',
    'CCᵣₑdᵤcₑ(min) = s + 2√(krt)',
    'CCₜₒₜₐₗ = r + 2s + t + 2√(krt)'
]) + ex('مثال Multi-way Join', [
    'اگر |R|=|T|=100 و k=4، انتخاب بهینه b=c=2 است.',
    ('calc', 'هر R دو بار + هر T دو بار + هر S یک بار\\nCC_reduce = s + 2×100 + 2×100 = s + 400')
]) + '''
<p><b>روش دو مرحله‌ای:</b> اگر احتمال تطابق R و S برابر p باشد، اندازه داده میانی تقریباً prs و
هزینه O(r+s+t+prs) است. انتخاب روش به اندازه روابط و خروجی میانی بستگی دارد.</p>
'''

d3 = h2('تکمله C — جزئیات Similarity، MinHash، LSH، PCY و CHARM', 'D3') + '''
<h3>Characteristic Matrix</h3>
<ul>
<li>هر سطر = یک shingle یکتا؛ هر ستون = یک سند</li>
<li>خانه 1 یعنی shingle در سند وجود دارد؛ ماتریس معمولاً بسیار sparse است.</li>
<li>AND دو ستون = اشتراک؛ OR = اجتماع.</li>
</ul>
<p><b>Set در برابر Bag:</b> Set تکرار shingle را حذف می‌کند؛ Bag فراوانی را نگه می‌دارد.
MinHash کلاسیک روی Set است.</p>

<h3>انتخاب k و Hash کردن Shingle</h3>
<ul>
<li>k خیلی کوچک → اسناد نامرتبط هم اشتراک زیاد دارند.</li>
<li>در لکچر: k≈5 برای سند کوتاه و k≈10 برای سند بلند.</li>
<li>می‌توان shingle را به شناسه ۴بایتی hash کرد تا فضا کم شود.</li>
<li>Collision می‌تواند شباهت را کمی بیش‌برآورد کند؛ فضای hash باید بزرگ باشد.</li>
</ul>

<h3>اثبات MinHash — جمله‌ای که حفظ می‌کنی</h3>
<p>در اجتماع C₁∪C₂، نخستین عضو permutation با احتمال مساوی هر عضو است. دو MinHash
فقط وقتی برابرند که نخستین عضو از اشتراک آمده باشد؛ بنابراین احتمال = |اشتراک|/|اجتماع|.</p>
''' + eq([
    'Ĵ(C₁,C₂) = (تعداد سطرهای برابر دو Signature) / K',
    'E[Ĵ] = J واقعی'
]) + '''
<p>هرچه تعداد توابع K بیشتر باشد، تخمین پایدارتر ولی حافظه/زمان بیشتر می‌شود.</p>

<h3>الگوریتم یک‌گذری MinHash بدون permutation</h3>
<ol>
<li>همه خانه‌های Signature را ∞ بگذار.</li>
<li>سطرهای ماتریس مشخصه را یک‌بار scan کن.</li>
<li>اگر سند C در سطر j مقدار 1 داشت، برای هر تابع i بنویس:
sig(C)[i] = min(sig(C)[i], hᵢ(j)).</li>
</ol>
''' + eq([
    'hₐ,ᵦ(x) = ((a·x + b) mod p) mod N      (p > N و اول)'
]) + '''

<h3>LSH: منطق AND/OR و S-Curve</h3>
<ul>
<li>داخل هر band: AND روی r سطر؛ همه باید برابر باشند.</li>
<li>بین bandها: OR؛ برابری فقط یک band کافی است.</li>
<li>منحنی احتمال نسبت به s شکل S دارد؛ آستانه تقریبی (1/b)^(1/r).</li>
<li>r بیشتر: FP کمتر، FN بیشتر. b بیشتر: FN کمتر، FP بیشتر.</li>
<li>Candidate بودن یعنی «ارزش بررسی دقیق دارد»، نه اینکه قطعاً مشابه است.</li>
<li>Exact Check، FP را حذف می‌کند؛ FN از دست‌رفته را نمی‌تواند برگرداند.</li>
</ul>
''' + eq([
    'False Negative = جفت واقعاً مشابه که candidate نشده',
    'False Positive = جفت نامشابه که candidate شده و بعداً رد می‌شود'
]) + '''

<h3>Normalizing و Mixed Attributes</h3>
''' + eq([
    'Min-Max: zᵢf = (xᵢf − min(xf)) / (max(xf) − min(xf))',
    'Z-score: zᵢf = (xᵢf − μf) / σf',
    'Mixed: d(i,j) = Σ δᶠᵢⱼ dᶠᵢⱼ / Σ δᶠᵢⱼ'
]) + '''
<p>δ=0 اگر مقدار missing باشد یا صفت دودویی نامتقارن و هر دو صفر باشند. صفت ترتیبی
با M مرتبه ابتدا به (rank−1)/(M−1) تبدیل و سپس مثل عددی محاسبه می‌شود.</p>
<p><b>هشدار:</b> 1−cosine یک dissimilarity رایج است، ولی لزوماً Metric نیست.
فاصله زاویه‌ای arccos(cosine) Metric مناسب‌تری است. فرمول LCS فقط برای درج/حذف است،
نه Levenshtein عمومی که جایگزینی هم دارد.</p>

<h3>PCY — جزئیات Bitmap</h3>
<ol>
<li>Pass1: تک‌اقلام را دقیق بشمار و همه جفت‌های هر basket را به B bucket hash کن.</li>
<li>بین دو pass: bucketهای با count≥minsup را در bitmap علامت بزن.</li>
<li>Pass2: جفت فقط اگر هر دو item frequent و bit باکت=1 باشد شمارش شود.</li>
</ol>
<p>باکت frequent تضمین نمی‌کند خود جفت frequent باشد (collision)، اما باکت infrequent
قطعاً نمی‌تواند جفت frequent داشته باشد.</p>

<h3>Closure، Tidset و Closed</h3>
''' + eq([
    't(X) = { TIDهایی که X در تراکنش آن‌هاست }',
    'i(Y) = { اقلام مشترک در همه TIDهای Y }',
    'closure: c(X) = i(t(X))',
    'X بسته است ⇔ c(X) = X'
]) + '''
<p>در کلاس itemsetهای با tidset یکسان، بزرگ‌ترین itemset همان Closed نماینده است.
Closed یک نمایش lossless برای support است؛ Maximal فشرده‌تر است ولی support زیرمجموعه‌ها را از دست می‌دهد.</p>

<h3>CHARM</h3>
<ul>
<li>نمایش عمودی itemset×tidset و prefix-equivalence class</li>
<li>t(X∪Y) = t(X)∩t(Y)؛ support = اندازه این اشتراک</li>
<li>تولید کاندید و شمارش support هم‌زمان است.</li>
<li>tidset برابر → اقلام همیشه باهم‌اند؛ در closure ادغام شوند.</li>
<li>رابطه زیرمجموعه tidsetها برای هرس شاخه‌ها استفاده می‌شود.</li>
</ul>

<h3>قواعد Non-redundant</h3>
<p>از Closedها یک basis کوچک از قواعد می‌سازیم که سایر قواعد قابل استنتاج باشند.
قواعد confidence=100٪ از closed بزرگ‌تر به کوچک‌ترند؛ قواعد کمتر از 100٪ به closed
superset حرکت می‌کنند.</p>
''' + ex('مثال‌های منبع', [
    ('calc', 'CW ⇒ C : support=5/6 ، confidence=5/5=1\\nCW ⇒ ACTW : support=3/6=0.5 ، confidence=3/5=0.6')
]) + '''
'''

d4 = h2('تکمله D — جزئیات کامل الگوریتم‌های خوشه‌بندی', 'D4') + '''
<h3>کاربردها و نیازها</h3>
<p>کاربرد: بخش‌بندی مشتری، بازیابی اطلاعات، زیست‌شناسی، داده فضایی، امنیت،
شناسایی outlier، پیش‌پردازش، جست‌وجوی وب و خلاصه‌سازی.</p>
<p>نیازها: مقیاس‌پذیری، انواع صفت، شکل دلخواه، دانش قبلی کم، تحمل نویز،
افزایشی و مستقل از ترتیب، ابعاد بالا، محدودیت کاربر و تفسیرپذیری.</p>

<h3>خوشه‌بندی سلسله‌مراتبی</h3>
<table>
<tr><th>روش</th><th>حرکت</th><th>شرح</th></tr>
<tr><td>AGNES</td><td>پایین→بالا</td><td>هر نقطه یک خوشه؛ نزدیک‌ترین‌ها ادغام</td></tr>
<tr><td>DIANA</td><td>بالا→پایین</td><td>همه یک خوشه؛ مرتب تقسیم</td></tr>
</table>
<p>خروجی معمولاً <b>Dendrogram</b> است. سه تصمیم: نمایش خوشه، فاصله دو خوشه،
و شرط توقف.</p>

<h3>Centroid در برابر Clustroid</h3>
''' + eq([
    'Centroid μC = (1/|C|) Σₓ∈C x',
    'Clustroid = یک نقطه واقعی که مجموع/بیشینه فاصله تا بقیه را کمینه کند'
]) + '''
<p>Centroid مناسب فضای اقلیدسی و ممکن است عضو واقعی داده نباشد. در اسناد/رشته‌ها
«میانگین» معنی ندارد، پس clustroid یا medoid می‌گیریم.</p>

<h3>Linkage، Radius و Diameter</h3>
''' + eq([
    'Single(C₁,C₂) = min d(x,y)',
    'Complete(C₁,C₂) = max d(x,y)',
    'Average(C₁,C₂) = [Σ d(x,y)] / (|C₁||C₂|)',
    'radius(C) = max d(x, μC)',
    'diameter(C) = max d(x,y)'
]) + '''
<ul>
<li>Single: مناسب شکل زنجیره‌ای، ولی اثر chaining و پل نویزی دارد.</li>
<li>Complete: خوشه فشرده، ولی حساس به outlier.</li>
<li>Average: تعادل بین دو روش.</li>
</ul>
<p>توقف: رسیدن به k، عبور radius/diameter از آستانه، افت چگالی، جهش کیفیت یا یک خوشه.</p>

<h3>K-Means — نکات امتحانی</h3>
''' + eq([
    'SSE = Σⱼ Σₓ∈Cⱼ ||x − μⱼ||²'
]) + '''
<ul>
<li>هر مرحله SSE را زیاد نمی‌کند، پس همگرا می‌شود؛ اما به بهینه محلی.</li>
<li>مقداردهی بهتر: مراکز دور ازهم، نمونه کوچک، یا چند اجرا و انتخاب کمترین SSE.</li>
<li>انتخاب k: Elbow؛ جایی که افزایش k دیگر بهبود زیاد نمی‌دهد.</li>
<li>ضعف: نیاز به k، حساس به init/outlier، نامناسب شکل غیرکروی و صفت اسمی.</li>
</ul>
''' + ex('چرا Outlier بد است؟', [
    ('calc', 'میانگین نقاط {1,2,3} = 2\\nبا اضافه‌شدن 100: میانگین = 26.5')
]) + '''

<h3>K-Medoids، PAM، CLARA، CLARANS</h3>
<ul>
<li><b>K-Medoids:</b> نماینده نقطه واقعی؛ فاصله دلخواه؛ مقاوم‌تر ولی گران‌تر.</li>
<li><b>PAM:</b> k medoid → تخصیص → امتحان تعویض medoid/non-medoid → قبول اگر هزینه کم شد.</li>
<li><b>CLARA:</b> چند نمونه تصادفی، PAM روی هر نمونه، ارزیابی روی کل داده؛ سریع ولی وابسته به نمونه.</li>
<li><b>CLARANS:</b> جواب‌های medoid را گراف می‌بیند و همسایه تصادفی را می‌گردد؛ کیفیت بهتر، هنوز پرهزینه.</li>
</ul>

<h3>BFR — فرض‌ها و سه مجموعه</h3>
<p>فضای اقلیدسی پُربعد؛ خوشه تقریباً نرمال؛ ابعاد مستقل؛ بیضی‌ها محورهم‌راستا.
هر خوشه با 2d+1 مقدار N، SUM، SUMSQ خلاصه می‌شود.</p>
<table>
<tr><th>مجموعه</th><th>معنی</th></tr>
<tr><td>DS (Discard Set)</td><td>با اطمینان عضو خوشه اصلی؛ خود نقاط دور ریخته و خلاصه حفظ می‌شود</td></tr>
<tr><td>CS (Compression Set)</td><td>گروه فشرده، ولی هنوز نزدیک هیچ DS نیست</td></tr>
<tr><td>RS (Retained Set)</td><td>نقاط منفرد/مشکوک که صریح نگه داشته می‌شوند</td></tr>
</table>
''' + eq([
    'Mahalanobis(x,C) = √ Σᵢ [ (xᵢ − μᵢ) / σᵢ ]²'
]) + '''
<p>مراحل: نمونه اولیه و DS → RS → خوشه‌کردن RS و ساخت CS → خواندن chunk →
نزدیک‌ها به DS، سپس CS، بقیه RS → ادغام CSها → در chunk آخر ادغام مناسب با DS.</p>

<h3>CURE</h3>
<ol>
<li>نمونه تصادفی در RAM</li>
<li>خوشه‌بندی سلسله‌مراتبی نمونه</li>
<li>انتخاب c نماینده که از هم دور باشند</li>
<li>حرکت هر نماینده کسری α به سمت centroid</li>
<li>فاصله خوشه‌ها = کمترین فاصله نماینده‌ها</li>
<li>تخصیص کل داده به نزدیک‌ترین نماینده</li>
</ol>
''' + eq([
    'r′ = r + α(μ − r)'
]) + '''
<p>نماینده‌های متعدد شکل خوشه را می‌گیرند؛ shrink به مرکز اثر outlier مرزی را کم می‌کند.</p>

<h3>DBSCAN — روابط دقیق</h3>
''' + eq([
    'N₍Eps₎(q) = { p | dist(p,q) ≤ Eps }',
    'Core ⇔ |N₍Eps₎(q)| ≥ MinPts'
]) + '''
<ul>
<li><b>Directly density-reachable:</b> p در همسایگی q و q یک Core باشد؛ لزوماً متقارن نیست.</li>
<li><b>Density-reachable:</b> زنجیره‌ای از دسترسی‌های مستقیم.</li>
<li><b>Density-connected:</b> نقطه o وجود دارد که p و q هر دو از آن قابل‌دسترسی‌اند؛ متقارن است.</li>
<li>با index فضایی تقریباً O(n log n)، بدون آن O(n²).</li>
<li>Eps کوچک → noise زیاد؛ Eps بزرگ → اتصال خوشه‌های جدا.</li>
<li>MinPts کم → نویز خوشه؛ MinPts زیاد → خوشه کوچک حذف.</li>
</ul>

<h3>OPTICS</h3>
''' + eq([
    'coreDist(p) = فاصله p تا MinPts-اُمین همسایه',
    'reachDist(p,q) = max(coreDist(q), dist(p,q))'
]) + '''
<p>به‌جای یک افراز، ترتیب نقاط و Reachability Plot می‌دهد. دره‌ها خوشه‌اند؛
دره عمیق‌تر یعنی چگالی بیشتر. مناسب‌تر از DBSCAN برای چگالی‌های متفاوت.</p>

<h3>STING و CLIQUE</h3>
<table>
<tr><th>روش</th><th>ایده</th><th>مزیت</th><th>ضعف</th></tr>
<tr><td>STING</td><td>شبکه سلسله‌مراتبی؛ در هر سلول count/mean/min/max</td><td>سریع، موازی، افزایشی</td><td>مرز پله‌ای/محورهم‌راستا</td></tr>
<tr><td>CLIQUE</td><td>سلول‌های متراکم در زیرفضای پُربعد؛ تولید زیرفضا با Apriori</td><td>کشف خودکار زیرفضا</td><td>حساس به اندازه grid و threshold</td></tr>
</table>

<h3>راهنمای انتخاب الگوریتم</h3>
<table>
<tr><th>شرایط</th><th>انتخاب</th></tr>
<tr><td>عددی، کروی، سریع</td><td>K-Means</td></tr>
<tr><td>پرت زیاد یا فاصله غیراقلیدسی</td><td>K-Medoids</td></tr>
<tr><td>داده عظیم و خوشه نرمال/محورهم‌راستا</td><td>BFR</td></tr>
<tr><td>شکل غیرکروی در فضای اقلیدسی</td><td>CURE</td></tr>
<tr><td>شکل دلخواه + نویز</td><td>DBSCAN</td></tr>
<tr><td>چگالی‌های متفاوت</td><td>OPTICS</td></tr>
<tr><td>ابعاد بالا و خوشه در بعضی ابعاد</td><td>CLIQUE</td></tr>
</table>
'''


def find_marks(pdf_path):
    doc = fitz.open(pdf_path)
    marks = {'_total': doc.page_count}
    keys = [
        'INDEX', 'CHEAT', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6',
        'S7', 'S8', 'S9', 'D1', 'D2', 'D3', 'D4', 'S10',
    ]
    for k in keys:
        marks[k] = None
        needle = f'[{k}]'
        for i in range(doc.page_count):
            if needle in doc[i].get_text():
                marks[k] = i + 1
                break
    return marks


def main():
    est = {
        k: 1 for k in [
            'INDEX', 'CHEAT', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6',
            'S7', 'S8', 'S9', 'D1', 'D2', 'D3', 'D4', 'S10',
        ]
    }
    est['_total'] = 12
    html = ''
    for it in range(6):
        body = '\n'.join([
            title,
            make_index(est, est['_total']),
            cheat,
            s1, s2, d1,
            s3, s4, s5, d2,
            s6, s7, s8, d3,
            s9, d4,
            s10,
        ])
        html = ('<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
                '<title>جزوه امتحانی داده‌های حجیم</title></head><body>'
                f'{body}</body></html>')
        pdf = OUT / 'جزوه_امتحانی_داده‌های_حجیم.pdf'
        HTML(string=html, base_url=str(OUT)).write_pdf(pdf, stylesheets=[WCSS(string=CSS)])
        new = find_marks(pdf)
        print('iter', it, {k: new[k] for k in est if k != '_total'}, 'total', new['_total'])
        if all(new.get(k) == est.get(k) for k in est if k != '_total'):
            print('STABLE')
            est = new
            break
        est = new

    (OUT / 'جزوه_امتحانی_داده‌های_حجیم.html').write_text(html, encoding='utf-8')

    # one-page cheat sheet with correct pages
    ch = f'''<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>چیت‌شیت</title>
<style>
@page {{ size: A4; margin: .8cm; }}
body {{ direction: rtl; font-family: "DejaVu Sans", Tahoma, sans-serif; font-size: 8.7pt; line-height: 1.28; }}
h1 {{ font-size: 1.08rem; color: #1a365d; border-bottom: 2px solid #2b6cb0; margin: 0 0 .25rem; }}
.eq {{
  direction: ltr !important; unicode-bidi: bidi-override !important; text-align: center;
  border: 1.5px solid #2d3748; border-radius: 5px; padding: .28rem; margin: .18rem 0;
  font-size: 11.5pt; font-weight: 700; background: #edf2f7; font-family: "DejaVu Sans", serif;
}}
.eq .line {{ display: block; }}
.where {{
  direction: rtl !important; unicode-bidi: embed !important; text-align: right;
  font-size: 7.6pt; font-weight: 400; border-top: 1px dashed #a0aec0; margin-top: .12rem; padding-top: .1rem;
  font-family: "DejaVu Sans", Tahoma, sans-serif;
}}
table {{ border-collapse: collapse; width: 100%; font-size: 7.8pt; margin: .12rem 0; }}
th, td {{ border: 1px solid #a0aec0; padding: .08rem .2rem; text-align: right; }}
th {{ background: #90cdf4; }}
.cols {{ display: table; width: 100%; }}
.col {{ display: table-cell; width: 50%; vertical-align: top; padding: 0 .12rem; }}
.note {{ background: #fffaf0; border-right: 3px solid #dd6b20; padding: .12rem .25rem; margin: .15rem 0; font-size: 7.8pt; }}
</style></head><body>
<h1>چیت‌شیت یک‌صفحه‌ای — داده‌های حجیم</h1>
<div class="note">پاسخ = تعریف + فرمول + مثال. شماره صفحات = جزوه کامل همین نسخه.</div>
<div class="cols"><div class="col">
<table>
<tr><th>مفهوم</th><th>یک خط</th></tr>
<tr><td>Shingle</td><td>دنباله k توکن متوالی</td></tr>
<tr><td>Jaccard</td><td>|A∩B| / |A∪B|</td></tr>
<tr><td>MinHash</td><td>Pr[هش برابر] = Jaccard</td></tr>
<tr><td>LSH</td><td>فقط candidateهای مشابه</td></tr>
<tr><td>Collab. Filtering</td><td>توصیه با شباهت کاربر/آیتم</td></tr>
<tr><td>Closed / Maximal</td><td>M ⊆ C ⊆ F</td></tr>
</table>
<div class="eq"><span class="line">TFᵢⱼ = fᵢⱼ / maxₖ(fₖⱼ)</span>
<span class="line">IDFᵢ = log₂(N / nᵢ)</span>
<span class="line">TF-IDF = TF × IDF</span>
<div class="where">مثال استاد: 0.1 × 3 = 0.3</div></div>
<div class="eq"><span class="line">J = |A∩B| / |A∪B|</span>
<span class="line">Pr[hπ(C1)=hπ(C2)] = J</span>
<span class="line">P = 1 − (1 − sʳ)ᵇ</span></div>
<div class="eq"><span class="line">L₂ = √Σ(xᵢ−yᵢ)²</span>
<span class="line">L₁ = Σ|xᵢ−yᵢ| &nbsp; L∞ = max|…|</span>
<span class="line">اسمی: (p − m) / p</span></div>
</div><div class="col">
<div class="eq"><span class="line">Map: (i , mᵢⱼ × vⱼ)</span>
<span class="line">Reduce: uᵢ = Σ (mᵢⱼ × vⱼ)</span>
<div class="where">مثال: U = [32, 26, 44]</div></div>
<div class="eq"><span class="line">sup(A⇒B) = sup(A∪B)</span>
<span class="line">conf = sup(A∪B) / sup(A)</span></div>
<table>
<tr><th>موضوع</th><th>صفحه جزوه</th></tr>
<tr><td>فهرست صفحات</td><td>{est["INDEX"]}</td></tr>
<tr><td>چیت‌شیت داخل جزوه</td><td>{est["CHEAT"]}</td></tr>
<tr><td>TF-IDF / Collaborative</td><td>{est["S1"]}</td></tr>
<tr><td>Cluster / Hadoop</td><td>{est["S2"]}</td></tr>
<tr><td>MapReduce</td><td>{est["S3"]}</td></tr>
<tr><td>Matrix × Vector</td><td>{est["S5"]}</td></tr>
<tr><td>Shingle / MinHash / LSH</td><td>{est["S6"]}</td></tr>
<tr><td>فاصله‌ها</td><td>{est["S7"]}</td></tr>
<tr><td>Apriori / Closed</td><td>{est["S8"]}</td></tr>
<tr><td>Clustering</td><td>{est["S9"]}</td></tr>
<tr><td><b>حل نمونه سوالات</b></td><td><b>{est["S10"]}</b></td></tr>
</table>
</div></div>
</body></html>'''
    (OUT / 'چیت_شیت.html').write_text(ch, encoding='utf-8')
    HTML(filename=str(OUT / 'چیت_شیت.html')).write_pdf(str(OUT / 'چیت_شیت.pdf'))
    shutil.copy2(OUT / 'چیت_شیت.pdf', OUT / 'برگه_فرمول_سریع.pdf')

    for f in ['جزوه_امتحانی_داده‌های_حجیم.pdf', 'چیت_شیت.pdf',
              'جزوه_امتحانی_داده‌های_حجیم.html', 'چیت_شیت.html']:
        shutil.copy2(OUT / f, ART / f)

    # verify
    doc = fitz.open(OUT / 'جزوه_امتحانی_داده‌های_حجیم.pdf')
    print('\n=== VERIFY INDEX ===')
    for i in range(doc.page_count):
        t = doc[i].get_text()
        if '[INDEX]' in t:
            print(t[:1600])
            break
    qa = Path('/tmp/pdfqa')
    qa.mkdir(exist_ok=True)
    for i in [0, 1, est['S5'] - 1, est['S10'] - 1]:
        doc[i].get_pixmap(matrix=fitz.Matrix(1.85, 1.85)).save(qa / f'p{i + 1}.png')
    print('FINAL PAGES', est)
    return est


if __name__ == '__main__':
    main()
