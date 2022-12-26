# esg_twitterbot

Step1. Docker run container use tensorflow image
```bash
docker run -d --gpus all --name esgTwitterPost -p 8889:8888 tensorflow/tensorflow:1.15.0-gpu-jupyter
```
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
Step4. Install & Setup Pyenv environment
```bash
curl https://pyenv.run | bash
pyenv install 3.7.16 && pyenv global 3.7.16
```
- Automatically install pyenv && Remember to restart shell

Step5. Pip install from the given requirements file  
 ```bash
 pip install -r requirements3.7.txt
 ```
Step6. Git clone this project in tensorflow-tutorials folder
  ```bash
  cd /tf/tensorflow-tutorials
  git clone https://github.com/advapplab/esg_twitterbot.git
  ```
Step7. Use crontab service to post tweet automatically
```bash
crontab -e
#Add a new crontab task
00 10 * * * cd /tf/tensorflow-tutorials/{YOUR_esg_twitterbot_FOLDER} &&  \
/root/.pyenv/shims/python esgTwitterPost.py > ./log/"esgDaily`date +\%Y\%m\%d`".log 2>&1
```
