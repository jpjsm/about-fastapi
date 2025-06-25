FROM python:3.12.7-bookworm
COPY --from=slx01008.live.dynatrace.com/linux/oneagent-codemodules:sdk / /
ENV LD_PRELOAD=/opt/dynatrace/oneagent/agent/lib64/liboneagentproc.so
RUN apt-get update && apt-get upgrade -y
RUN  python3 -m pip install --upgrade pip
RUN apt-get install -y python3-venv
WORKDIR /APP
RUN python3 -m venv .
RUN . bin/activate
RUN pip install "fastapi[standard]"
RUN pip install "psycopg[binary,pool]"
RUN pip install autodynatrace
ENV AUTOWRAPT_BOOTSTRAP=autodynatrace
ENV DT_TENANT=slx01008
ENV DT_TENANTTOKEN=UxLguU1R3FfuIFay
ENV DT_CONNECTION_POINT=https://sg-us-west-2-44-242-35-15-prod59-oregon.live.dynatrace.com/communication;https://sg-us-west-2-54-185-86-96-prod59-oregon.live.dynatrace.com/communication;https://sg-us-west-2-34-211-84-234-prod59-oregon.live.dynatrace.com/communication;https://slx01008.live.dynatrace.com:443
COPY ./src/* .
ENTRYPOINT [ "python3", "main.py" ]