FROM openjdk:17-jdk-slim
ARG JAR

WORKDIR /app
COPY $JAR /app/app.jar
RUN touch /app/empty-vault.properties

ENV JVM_ARGS=""

ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar app.jar"]