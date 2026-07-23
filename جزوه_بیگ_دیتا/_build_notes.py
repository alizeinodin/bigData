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


def find_marks(pdf_path):
    doc = fitz.open(pdf_path)
    marks = {'_total': doc.page_count}
    keys = ['INDEX', 'CHEAT', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']
    for k in keys:
        marks[k] = None
        needle = f'[{k}]'
        for i in range(doc.page_count):
            if needle in doc[i].get_text():
                marks[k] = i + 1
                break
    return marks


def main():
    est = {k: 1 for k in ['INDEX', 'CHEAT', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']}
    est['_total'] = 12
    html = ''
    for it in range(6):
        body = '\n'.join([
            title,
            make_index(est, est['_total']),
            cheat, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10,
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
