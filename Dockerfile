FROM openjdk:8

ENV PROJECT_NAME dni
ENV DIST_NAME $PROJECT_NAME-1.0-SNAPSHOT

EXPOSE 8080

COPY $DIST_NAME.tar /app/
WORKDIR /app
RUN tar -xvf $DIST_NAME.tar

COPY config.json /app/$DIST_NAME

WORKDIR /app/$DIST_NAME
CMD ["bash", "bin/dni"]
