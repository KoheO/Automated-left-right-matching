# 必要なライブラリをロード
library(nat)
library(nat.nblast)
library(dplyr)

# ディレクトリのパスを定義
right_flipped_dir <- "C:/Users/jtcn0/MyProject/right_swc_files"
left_output_dir <- "C:/Users/jtcn0/MyProject/left_swc_files"
min_size = 10

# NBLASTスコアを計算して保存する関数
process_neurons <- function(right_flipped_dir, left_output_dir, output_file = "C:/Users/jtcn0/MyProject/nblast_bidirectional_scores.csv") {
  results <- list()
  
  # 右側ニューロンのSWCファイルを取得
  right_files <- list.files(right_flipped_dir, pattern = "\\.swc$", full.names = TRUE)
  if (length(right_files) == 0) {
    cat("右側ニューロンのファイルが見つかりません。\n")
    return(NULL)
  }
  
  # 左側ニューロンのSWCファイルを取得
  left_files <- list.files(left_output_dir, pattern = "\\.swc$", full.names = TRUE)
  if (length(left_files) == 0) {
    cat("左側ニューロンのファイルが見つかりません。\n")
    return(NULL)
  }

  # 右側ニューロンごとにループ
  for (right_file in right_files) {
    cat("右側ニューロンを処理中:", basename(right_file), "\n")
    
    # 右側ニューロンを読み込む
    right_neuron <- tryCatch(
      read.neuron(right_file),
      error = function(e) {
        cat("右側ニューロンの読み込みに失敗:", basename(right_file), "\n")
        return(NULL)
      }
    )
    if (is.null(right_neuron)) next
    
    # 左側ニューロンごとにループ
    for (left_file in left_files) {
      cat("左側ニューロンを処理中:", basename(left_file), "\n")
      
      # 左側ニューロンを読み込む
      left_neuron <- tryCatch(
        read.neuron(left_file),
        error = function(e) {
          cat("左側ニューロンの読み込みに失敗:", basename(left_file), "\n")
          return(NULL)
        }
      )
      if (is.null(left_neuron)) next
      
      # ニューロンリストを作成
      neurons <- neuronlist(right_neuron, left_neuron)
      
      # NBLAST比較（個別比較）
      nblast_score <- tryCatch(
        nblast(neurons[[1]], neurons[[2]]),  # 個別に比較
        error = function(e) {
          cat("NBLASTスコア計算中にエラー:", e$message, "\n")
          return(NULL)
        }
      )
      if (is.null(nblast_score)) next
      
      # デバッグ: NBLASTスコアを確認
      cat("NBLASTスコア:", basename(right_file), "vs", basename(left_file), "=", nblast_score, "\n")
      
      # スコアをリストに追加
      if (!is.null(nblast_score)) {
        results <- append(results, list(data.frame(
          Right_Flipped_Neuron = basename(right_file),
          Left_Neuron = basename(left_file),
          NBLAST_Score = nblast_score  # 個別スコアを追加
        )))
      }
    }
  }
  
  # 結果をデータフレームに変換
  if (length(results) == 0) {
    cat("処理結果が空です。入力ファイルやパラメータを確認してください。\n")
    return(NULL)
  }
  results_df <- do.call(rbind, results)
  
  # 結果をCSVに保存
  tryCatch(
    {
      write.csv(results_df, output_file, row.names = FALSE)
      cat("NBLASTスコアを保存しました:", output_file, "\n")
    },
    error = function(e) {
      cat("CSVファイルの保存中にエラー:", e$message, "\n")
    }
  )
}

# 関数を実行
process_neurons(right_flipped_dir, left_output_dir)
