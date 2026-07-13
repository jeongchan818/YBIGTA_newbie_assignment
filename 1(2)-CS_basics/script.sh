# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
if ! command -v conda &> /dev/null; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    source $HOME/miniconda/bin/activate
else
    eval "$(conda shell.bash hook)"
fi

# Conda 환경 생성 및 활성화
conda create -n myenv python=3.10 -c conda-forge -y
conda activate myenv

## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
pip install mypy

# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    get_num=$(echo "$file" | grep -oE '[0-9]+' | tail -n 1)

    input_file="../input/${get_num}_input"
    output_file="../output/${get_num}_output"

    python "$file" < "$input_file" > "$output_file"
done

# mypy 테스트 실행 및 mypy_log.txt 저장
mypy . > ../mypy_log.txt || true

# conda.yml 파일 생성
conda env export > ../conda.yml

# 가상환경 비활성화
conda deactivate
cd ..