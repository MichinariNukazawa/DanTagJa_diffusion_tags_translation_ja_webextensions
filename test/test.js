
// 翻訳テストケース
'  1girl, flower' + // 先頭空白、翻訳のない単語、翻訳のある単語
' black hat  brown hair  ' + // 色などが先頭についた単語,単語間の連続した空白
'' + // 何も入っていない行
' 　' + // 空文字しか入っていない行
'long_sleeves hair tie upper body' + // '_'でつながったidiom, 空白で区切りの曖昧なidiomの連続
'(worried:1.2), (sailor collar) {sailor collar} {{sailor collar}}' // 様々に囲われた単語やidiom
// なにか'-'で連結している単語
