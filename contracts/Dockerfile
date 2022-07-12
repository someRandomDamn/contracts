FROM mcr.microsoft.com/dotnet/sdk:6.0-focal

RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update  \
    && apt-get install git  \
    && apt-get install curl  \
    && apt-get install -y libsnappy-dev libleveldb-dev  \
    && apt-get install -y python3.8 python3-distutils python3-pip python3-apt

RUN apt-get install -y unzip libleveldb-dev sqlite3 libsqlite3-dev libunwind8-dev

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN pip install --upgrade "pip>=19.3"

WORKDIR /usr/src

RUN wget https://github.com/neo-project/neo-node/releases/download/v3.3.1/neo-cli-linux-x64.zip
RUN unzip neo-cli-linux-x64.zip && rm neo-cli-linux-x64.zip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/simplitech/neo-devpack-dotnet.git -b v3.2.1
RUN dotnet build ./neo-devpack-dotnet/src/Neo.TestEngine/Neo.TestEngine.csproj

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/neo3/contracts"
