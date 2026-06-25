"""Enhance quiz result UI to show wrong answers with mark scheme info"""
import re

with open('index.html', 'r', encoding='utf-8', errors='surrogatepass') as f:
    content = f.read()

# Find and replace the quiz result rendering block
old = r"""html+='<div class="q-result '+(correct?'correct':'wrong')+'"><div class="qr-label">'+(correct?'\u2705 \u6b63\u786e\uff01':'\u274c \u9519\u8bef')+'</div><div class="qr-explain">'+q.explain+'</div>';
      if(!correct)html+='<div class="qr-improve">\ud83d\udca1 '+q.improve+'</div>';
      html+='</div>';"""

new = r"""var letters='ABCD';
      html+='<div class="q-result '+(correct?'correct':'wrong')+'"><div class="qr-label">'+(correct?'\u2705 \u6b63\u786e\uff01':'\u274c \u9519\u8bef')+'</div>';
      if(!correct&&q.type==='mc'){
        var yourIdx=quizState.answers[i];
        var yourAns=(yourIdx!==undefined&&yourIdx!==null)?letters[yourIdx]+'. '+q.options[yourIdx]:'\u672a\u4f5c\u7b54';
        var corAns=letters[q.answer]+'. '+q.options[q.answer];
        html+='<div class="qr-yourAns">\ud83d\udc64 \u4f60\u9009\u4e86: <b>'+yourAns+'</b></div>';
        html+='<div class="qr-corAns">\u2705 \u6b63\u786e\u7b54\u6848: <b>'+corAns+'</b></div>';
      }
      html+='<div class="qr-explain">\ud83d\udcdd \u89e3\u6790: '+q.explain+'</div>';
      if(q.paper)html+='<div class="qr-ms">\ud83d\udcc4 \u8bc4\u5206\u6807\u51c6 ('+q.paper+', '+(q.marks||1)+'\u5206): '+(q.mscheme||q.explain)+'</div>';
      if(!correct)html+='<div class="qr-improve">\ud83d\udca1 \u6539\u8fdb: '+q.improve+'</div>';
      html+='</div>';"""

if old in content:
    content = content.replace(old, new)
    print("Patched quiz result rendering")
else:
    print("WARN: old string not found, trying line-by-line approach")
    # Find the line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "qr-improve" in line and "q.improve" in line:
            print(f"Found at line {i}")
            break

with open('index.html', 'w', encoding='utf-8', errors='surrogatepass') as f:
    f.write(content)
print("Done")
