# ポケポケプロジェクト

## 各処理
エナジーは配列で処理する。


## クラス

- **Game**
    
    ゲームの処理
    
    1. 準備フェーズ
        1. 各プレイヤーにカードを配る（種ポケモンが最低1枚あるように)
        2. プレイヤーに準備フェーズであることを伝える。
    2. ターン処理（勝敗判定を含む）
        
        ターン変化条件
        
        ターン終了
        
        ポケモンカードによる攻撃
        
        これ以降1ターンの流れについて考えればよくなる。
        
    3. カード処理
    4. エナジー処理
    5. ダメージ処理
        
        ダメージを受けた際にポケモンカードのHPを減らす。
        
    6. サイド処理
        
        ポケモンのHPがダメージを
        
    7. 手札処理
        
        毎ターン一枚ずつ山札から引く
        
        シャッフルすることができる
        
- **Player**
    
    準備フェーズの行動
    
    1. バトル場に種ポケモンを出す
    2. ベンチに種ポケモンを出す
    
    ノーマルフェーズの行動
    
    1. 攻撃
        1. 必要エナジーがちゃんとそろっていること
    2. 逃げる
        1. 必要なエナジーがちゃんとそろっていること
        2. このターンで逃げるをせんたくしていないこと
    3. 次のターン
        1. 条件なし
    4. 道具カードを使う
    5. 種ポケモンカードを使う（ベンチに）
        1. ベンチに枠がある
    6. 進化先ポケモンカードを使う
        1. このターンでそのポケモンが進化していないこと
        2. 手札に進化先ポケモンカードがあるということ
    7. 道具を使う
        1. 条件なし
    8. エナジーをつける
        1. 割り振られた
    9. ベンチからポケモンを出す
        1. 直前にバトル場のポケモンがいなくなっている。
    
- **TrainerCard**
    
    aaa
    
- **ToolCard**
    
    aaa
    
- **PockemonCard**
    
    type: Enum
    
    health_point: Integer
    
    weak_type: Enum
    
    is_ex: bool
    
    is_seed: bool
    
    can_evolve: bool
    
    energies: List[Energy]
    
    prev_card: None | Card
    
    next_card: None | Card
    
    def can_move1( game: Game )
    
    def can_move2( game: Game )
    
    def move1( game: Game  )
    
    def move2( game: Game )
    
    def can_ability( game: Game)
    
    def ability( game: Game )
    
    def can_escape( game: Game )
    
    def escape( game: Game )
    
    これを親クラスとした子クラス（各ポケモン）を作成する。