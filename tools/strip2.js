// v209 빌드: 줄 수 다이어트 — JS는 압축(이름·로직 그대로, 공백/주석만 제거, 1000자 단위 줄바꿈),
// CSS/HTML은 공백 정리 후 1000자 단위로 줄바꿈. dothome 엔티티 보호(\x26)와 quote_style:3은 기존과 동일
const fs = require('fs');
const { minify } = require('terser');
const MAX = 1000;
function wrapAt(text, re){ // re: 줄을 끊어도 안전한 지점(정규식, 매치 끝에서 끊음)
  let out = '', line = '', last = 0, m;
  re.lastIndex = 0;
  while((m = re.exec(text))){
    const piece = text.slice(last, m.index + m[0].length); last = m.index + m[0].length;
    if(line.length + piece.length > MAX && line.length){ out += line + '\n'; line = ''; }
    line += piece;
  }
  line += text.slice(last);
  return out + line;
}
(async () => {
  const [,, inPath, outPath] = process.argv;
  let html = fs.readFileSync(inPath, 'utf8');
  const parts = []; const re = /<script>([\s\S]*?)<\/script>/g; let last = 0, m;
  while((m = re.exec(html))){ parts.push({type:'html', text: html.slice(last, m.index)}); parts.push({type:'js', text: m[1]}); last = re.lastIndex; }
  parts.push({type:'html', text: html.slice(last)});
  for(const p of parts){
    if(p.type === 'js'){
      const r = await minify(p.text, { compress:false, mangle:false, format:{ comments:false, beautify:false, max_line_len: MAX, quote_style:3 } });
      const safe = r.code.replace(/&(amp|lt|gt|quot|nbsp|apos|#39|#x27);/g, '\\x26$1;');
      p.text = '<script>\n' + safe + '\n</script>';
    } else {
      let t = p.text.replace(/<!--[\s\S]*?-->/g, '');
      // <style> 블록: 주석 제거 + 공백 압축 + '}' 뒤에서 줄바꿈
      t = t.replace(/<style>([\s\S]*?)<\/style>/g, (a, css) => '<style>\n' + wrapAt(css.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\s+/g, ' ').trim(), /\}/g) + '\n</style>');
      // 나머지 HTML: textarea/pre 내용은 보존, 그 외 공백 압축 후 '>' 뒤에서 줄바꿈
      const keep = []; t = t.replace(/<(textarea|pre)[\s\S]*?<\/\1>/g, s => { keep.push(s); return `\u0000${keep.length-1}\u0000`; });
      t = t.split(/(<style>[\s\S]*?<\/style>)/).map(seg => seg.startsWith('<style>') ? seg : wrapAt(seg.replace(/\s+/g, ' '), />/g)).join('');
      t = t.replace(/\u0000(\d+)\u0000/g, (a, i) => keep[+i]);
      p.text = t;
    }
  }
  fs.writeFileSync(outPath, parts.map(p => p.text).join(''));
})();
