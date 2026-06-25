"""Patch submitQuiz to include paper/mscheme in wrong answer recording"""
with open('index.html', 'r', encoding='utf-8', errors='surrogatepass') as f:
    c = f.read()

old = "wqData.push({id:Date.now()+i,subject:subjKey(quizState.subject),chapter:quizState.topic,question:q.text,mistake:userAns,correct:q.answer+' \\u2014 '+q.explain,date:new Date().toISOString().slice(0,10),mastered:false,attempts:0,lastAttempt:null,improve:q.improve});"

new = """var corText=q.type==='mc'?(String.fromCharCode(65+q.answer)+'. '+q.options[q.answer]):(q.answer+'');
      if(q.paper)corText+=' [\\ud83d\\udcc4'+q.paper+', '+(q.marks||1)+'\\u5206: '+(q.mscheme||'')+']';
      wqData.push({id:Date.now()+i,subject:subjKey(quizState.subject),chapter:quizState.topic,question:q.text,mistake:userAns,correct:corText+' \\u2014 '+q.explain,date:new Date().toISOString().slice(0,10),mastered:false,attempts:0,lastAttempt:null,improve:q.improve});"""

if old in c:
    c = c.replace(old, new)
    print("Patched submitQuiz wrong answer recording")
else:
    print("WARN: old string not found!")
    # Debug: find it
    idx = c.find("wqData.push")
    if idx >= 0:
        print(f"Found wqData.push at position {idx}")
        print(repr(c[idx:idx+300]))

with open('index.html', 'w', encoding='utf-8', errors='surrogatepass') as f:
    f.write(c)
print("Done")
