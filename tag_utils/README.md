


----

タググループの一覧ページをrootに再帰的にタグページを収集したが、実際にはタグページ下にぶら下がっているタグもあった。
(色＋モノ等. ex."black pantyhose" https://danbooru.donmai.us/wiki_pages/black_pantyhose )
wiki上で孤立したタグページもあるかもしれない。
タグページ一覧みたいなものをさがしてタグページ収集するべきだったか？
（その場合タググループ情報が得られないが）


> cowboy shot<中景镜头> 
など、ちょくちょく中文が混じっている。（対応しようもないし、まあ良しとする）

>    "tag_name": "Up",
>    "taggroup": "Tag group:Dogs",
>    "related_tags": [
>      "カールじいさんの空飛ぶ家"
>    ],
> https://danbooru.donmai.us/wiki_pages/up

まず
```
Ambiguous tag. For a list of tags containing up, see here.
This tag is deprecated and can't be added to new posts.
```

ついでになぜDogsタグかといえば、DogsTagのページに「犬的なキャラ（の登場する作品一覧）」という一覧があるから。


> multiple girls<全裸群像>
> https://danbooru.donmai.us/wiki_pages/multiple_girls?z=1
これはwiki側が間違っているか中文がそういうものということと思われる。

>  {
>    "tag_name": "flower",
>    "taggroup": "List of Vocaloid derivatives",
>    "related_tags": [
>      "v_flower",
>      "vflower"
>    ],
同名タグも存在する模様。統計は取っていないがおそらく他にもある。
例はボカロ曲にある"flower"

TODO スクレイピングで取得したページのHTMLをファイル保存してキャッシュに使う処理の追加
（中断・再解析での負担を減らす）（高頻度では更新されない想定）
TODO related_tagsに英文が入っているタグがある？ 調査して日本語文を探して最初に持ってくる等の対応を行う
TODO Haloのrelated_tagsに英文が入っているがwikiページ上ではそうなっていない。

