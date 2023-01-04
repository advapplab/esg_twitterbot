# esg_twitterbot
## Brief Intro Folder tree
```bash
.
├── README.md---
├── download_finetune_model.py # Download finetune model from S3
├── esgBERT_input # Read everyday ESG news from MongoDB
│   ├── esgNews_{date}.tsv # Model input (only content)
│   ├── esgNews_{date}_full.tsv # Contain content, url, datasource
├── esgBERT_output 
│   ├── esgNews_{date}_table.csv # Merge esgBERT output into a 35 key issues table
│   ├── esgNews_{date}_choose_sentences.csv # The GPT-3 input sentences
├── esgTwitterPost.py # Main python script
├── import_data # esgBERT necessary files
│   ├── bert_config.json
│   ├── label.json
│   ├── modeling.py
│   ├── optimization.py
│   ├── run_classifier_test.py
│   ├── tokenization.py
│   └── vocab.txt
├── log
│   ├── esgDaily{date}.log
├── modules
│   ├── PredictModel.py # esgBERT model
│   ├── credential.json # AWS, MongoDB, OpenAI, Twitter key (Owner: wei)
│   ├── mongodb_forRead.py # MongoDB API
│   ├── mongodb_static_data.py # MongoDB connection
│   └── secret.py # OpenAI, Twitter key setting
├── predict_folder_config.json # Folder path using by esgBERT
└── requirements3.7.txt
```
## Installing Step
Step1. Docker run container use tensorflow image
```bash
# --gpus all command will cause error if your pc has no gpu!
docker run -d --gpus all --name esgTwitterPost -p YOURPORT:8888 tensorflow/tensorflow:1.15.0-gpu-jupyter
```
Step1.5. Open a container terminal to do Step 2 ~ 8

Step2.  Linux APT NO_PUBKEY cause GPG error solution
```bash
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC && apt update -y
```
- Initial image would get a missing key error
- You can apt update after getting public key

Step3. Install packages
```bash
apt install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev git cron nano wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev \
libxmlsec1-dev libffi-dev liblzma-dev libgirepository1.0-dev libcairo2 libcairo2-dev
```
Step4. Install (would take about 10 minutes)&  Setup Pyenv environment
```bash
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && echo 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile && echo 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.profile
bash # Restarting the shell can read new .bashrc
pyenv install 3.7.16 && pyenv global 3.7.16
```
- Automatically install pyenv && Remember to restart shell

Step5. Git clone this project in tf folder
 ```bash
 git clone https://github.com/advapplab/esg_twitterbot.git
 cd esg_twitterbot
 ```
Step6. Use jupyter notebook upload credential.json(from Wei) into modules folder 

Step7. Pip install from the given requirements file && Execute python script to download finetune model (About 2hrs)
  ```bash
  pip install -r requirements3.7.txt
  python download_finetune_model.py
  ```
Step8. Use crontab service to post tweet automatically
```bash
crontab -e
#Add a new crontab task
00 10 * * * cd /tf/esg_twitterbot &&  \
/root/.pyenv/shims/python esgTwitterPost.py > ./log/"esgDaily`date +\%Y\%m\%d`".log 2>&1
```
