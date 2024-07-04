@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%"=="" @echo off
@rem ##########################################################################
@rem
@rem  launcher startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
@rem This is normally unused
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%..

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and LAUNCHER_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH. 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME% 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\lib\launcher.jar;%APP_HOME%\lib\data-dashboard-local.jar;%APP_HOME%\lib\control-plane-api-client-0.7.0.jar;%APP_HOME%\lib\control-plane-api-0.7.0.jar;%APP_HOME%\lib\control-plane-core-0.7.0.jar;%APP_HOME%\lib\dsp-0.7.0.jar;%APP_HOME%\lib\configuration-filesystem-0.7.0.jar;%APP_HOME%\lib\iam-mock-0.7.0.jar;%APP_HOME%\lib\management-api-0.7.0.jar;%APP_HOME%\lib\transfer-data-plane-signaling-0.7.0.jar;%APP_HOME%\lib\transfer-pull-http-receiver-0.7.0.jar;%APP_HOME%\lib\validator-data-address-http-data-0.7.0.jar;%APP_HOME%\lib\edr-cache-api-0.7.0.jar;%APP_HOME%\lib\edr-store-core-0.7.0.jar;%APP_HOME%\lib\edr-store-receiver-0.7.0.jar;%APP_HOME%\lib\data-plane-self-registration-0.7.0.jar;%APP_HOME%\lib\data-plane-selector-api-0.7.0.jar;%APP_HOME%\lib\data-plane-selector-core-0.7.0.jar;%APP_HOME%\lib\data-plane-control-api-0.7.0.jar;%APP_HOME%\lib\data-plane-public-api-v2-0.7.0.jar;%APP_HOME%\lib\data-plane-core-0.7.0.jar;%APP_HOME%\lib\data-plane-http-0.7.0.jar;%APP_HOME%\lib\api-observability-0.7.0.jar;%APP_HOME%\lib\control-plane-sql-0.7.0.jar;%APP_HOME%\lib\sql-pool-apache-commons-0.7.0.jar;%APP_HOME%\lib\data-plane-migration-0.7.2.jar;%APP_HOME%\lib\control-plane-migration-0.7.2.jar;%APP_HOME%\lib\contract-negotiation-store-sql-0.7.0.jar;%APP_HOME%\lib\transfer-process-store-sql-0.7.0.jar;%APP_HOME%\lib\sql-lease-0.7.0.jar;%APP_HOME%\lib\postgresql-migration-lib-0.7.2.jar;%APP_HOME%\lib\asset-index-sql-0.7.0.jar;%APP_HOME%\lib\contract-definition-store-sql-0.7.0.jar;%APP_HOME%\lib\policy-definition-store-sql-0.7.0.jar;%APP_HOME%\lib\sql-core-0.7.0.jar;%APP_HOME%\lib\transaction-local-0.7.0.jar;%APP_HOME%\lib\transfer-data-plane-0.7.0.jar;%APP_HOME%\lib\federated-catalog-core-0.7.0.jar;%APP_HOME%\lib\federated-catalog-api-0.7.0.jar;%APP_HOME%\lib\dsp-catalog-0.7.0.jar;%APP_HOME%\lib\dsp-catalog-http-dispatcher-0.7.0.jar;%APP_HOME%\lib\dsp-negotiation-0.7.0.jar;%APP_HOME%\lib\dsp-negotiation-http-dispatcher-0.7.0.jar;%APP_HOME%\lib\dsp-transfer-process-0.7.0.jar;%APP_HOME%\lib\dsp-transfer-process-http-dispatcher-0.7.0.jar;%APP_HOME%\lib\dsp-http-core-0.7.0.jar;%APP_HOME%\lib\data-plane-signaling-client-0.7.0.jar;%APP_HOME%\lib\crawler-core-0.7.0.jar;%APP_HOME%\lib\connector-core-0.7.0.jar;%APP_HOME%\lib\junit-0.7.0.jar;%APP_HOME%\lib\data-plane-client-0.7.0.jar;%APP_HOME%\lib\http-lib-0.7.0.jar;%APP_HOME%\lib\http-spi-0.7.0.jar;%APP_HOME%\lib\control-plane-api-client-spi-0.7.0.jar;%APP_HOME%\lib\control-plane-aggregate-services-0.7.0.jar;%APP_HOME%\lib\asset-api-0.7.0.jar;%APP_HOME%\lib\catalog-api-0.7.0.jar;%APP_HOME%\lib\contract-agreement-api-0.7.0.jar;%APP_HOME%\lib\contract-definition-api-0.7.0.jar;%APP_HOME%\lib\contract-negotiation-api-0.7.0.jar;%APP_HOME%\lib\policy-definition-api-0.7.0.jar;%APP_HOME%\lib\transfer-process-api-0.7.0.jar;%APP_HOME%\lib\dsp-http-api-configuration-0.7.0.jar;%APP_HOME%\lib\dsp-version-http-api-0.7.0.jar;%APP_HOME%\lib\dsp-catalog-transform-0.7.0.jar;%APP_HOME%\lib\dsp-catalog-http-api-0.7.0.jar;%APP_HOME%\lib\dsp-negotiation-http-api-0.7.0.jar;%APP_HOME%\lib\dsp-negotiation-transform-0.7.0.jar;%APP_HOME%\lib\dsp-transfer-process-http-api-0.7.0.jar;%APP_HOME%\lib\dsp-transfer-process-transform-0.7.0.jar;%APP_HOME%\lib\dsp-http-spi-0.7.0.jar;%APP_HOME%\lib\dsp-spi-0.7.0.jar;%APP_HOME%\lib\control-plane-spi-0.7.0.jar;%APP_HOME%\lib\control-api-configuration-0.7.0.jar;%APP_HOME%\lib\management-api-configuration-0.7.0.jar;%APP_HOME%\lib\api-core-0.7.0.jar;%APP_HOME%\lib\auth-spi-0.7.0.jar;%APP_HOME%\lib\http-0.7.0.jar;%APP_HOME%\lib\jersey-core-0.7.0.jar;%APP_HOME%\lib\jetty-core-0.7.0.jar;%APP_HOME%\lib\data-plane-signaling-transform-0.7.0.jar;%APP_HOME%\lib\jersey-providers-lib-0.7.0.jar;%APP_HOME%\lib\web-spi-0.7.0.jar;%APP_HOME%\lib\store-lib-0.7.0.jar;%APP_HOME%\lib\query-lib-0.7.0.jar;%APP_HOME%\lib\control-plane-catalog-0.7.0.jar;%APP_HOME%\lib\control-plane-contract-0.7.0.jar;%APP_HOME%\lib\control-plane-transfer-0.7.0.jar;%APP_HOME%\lib\transfer-spi-0.7.0.jar;%APP_HOME%\lib\control-plane-transform-0.7.0.jar;%APP_HOME%\lib\federated-catalog-spi-0.7.0.jar;%APP_HOME%\lib\crawler-spi-0.7.0.jar;%APP_HOME%\lib\catalog-spi-0.7.0.jar;%APP_HOME%\lib\asset-spi-0.7.0.jar;%APP_HOME%\lib\control-plane-policies-lib-0.7.0.jar;%APP_HOME%\lib\contract-spi-0.7.0.jar;%APP_HOME%\lib\transfer-data-plane-spi-0.7.0.jar;%APP_HOME%\lib\transform-lib-0.7.0.jar;%APP_HOME%\lib\data-plane-client-embedded-0.7.0.jar;%APP_HOME%\lib\data-plane-selector-spi-0.7.0.jar;%APP_HOME%\lib\data-plane-util-0.7.0.jar;%APP_HOME%\lib\data-plane-spi-0.7.0.jar;%APP_HOME%\lib\validator-lib-0.7.0.jar;%APP_HOME%\lib\validator-spi-0.7.0.jar;%APP_HOME%\lib\data-plane-http-spi-0.7.0.jar;%APP_HOME%\lib\data-address-http-data-spi-0.7.0.jar;%APP_HOME%\lib\edr-store-spi-0.7.0.jar;%APP_HOME%\lib\policy-spi-0.7.0.jar;%APP_HOME%\lib\json-ld-0.7.0.jar;%APP_HOME%\lib\token-core-0.7.0.jar;%APP_HOME%\lib\token-spi-0.7.0.jar;%APP_HOME%\lib\state-machine-lib-0.7.0.jar;%APP_HOME%\lib\keys-lib-0.7.0.jar;%APP_HOME%\lib\crypto-common-lib-0.7.0.jar;%APP_HOME%\lib\identity-did-spi-0.7.0.jar;%APP_HOME%\lib\keys-spi-0.7.0.jar;%APP_HOME%\lib\json-ld-lib-0.7.0.jar;%APP_HOME%\lib\json-ld-spi-0.7.0.jar;%APP_HOME%\lib\transform-spi-0.7.0.jar;%APP_HOME%\lib\policy-engine-lib-0.7.0.jar;%APP_HOME%\lib\core-utils-0.7.2.jar;%APP_HOME%\lib\identity-trust-spi-0.7.0.jar;%APP_HOME%\lib\policy-engine-spi-0.7.0.jar;%APP_HOME%\lib\secrets-spi-0.7.0.jar;%APP_HOME%\lib\json-lib-0.7.0.jar;%APP_HOME%\lib\core-spi-0.7.0.jar;%APP_HOME%\lib\postgresql-42.7.3.jar;%APP_HOME%\lib\flyway-database-postgresql-10.13.0.jar;%APP_HOME%\lib\flyway-core-10.13.0.jar;%APP_HOME%\lib\boot-0.7.0.jar;%APP_HOME%\lib\boot-lib-0.7.0.jar;%APP_HOME%\lib\junit-base-0.7.0.jar;%APP_HOME%\lib\verifiable-credentials-spi-0.7.0.jar;%APP_HOME%\lib\boot-spi-0.7.0.jar;%APP_HOME%\lib\failsafe-okhttp-3.3.2.jar;%APP_HOME%\lib\failsafe-3.3.2.jar;%APP_HOME%\lib\jersey-container-servlet-3.1.6.jar;%APP_HOME%\lib\jersey-container-servlet-core-3.1.6.jar;%APP_HOME%\lib\jersey-server-3.1.6.jar;%APP_HOME%\lib\jersey-media-json-jackson-3.1.6.jar;%APP_HOME%\lib\jersey-media-multipart-3.1.6.jar;%APP_HOME%\lib\jersey-hk2-3.1.6.jar;%APP_HOME%\lib\jersey-client-3.1.6.jar;%APP_HOME%\lib\jersey-common-3.1.6.jar;%APP_HOME%\lib\jersey-entity-filtering-3.1.6.jar;%APP_HOME%\lib\jakarta.ws.rs-api-4.0.0.jar;%APP_HOME%\lib\swagger-jaxrs2-jakarta-2.2.21.jar;%APP_HOME%\lib\util-lib-0.7.0.jar;%APP_HOME%\lib\transaction-spi-0.7.0.jar;%APP_HOME%\lib\opentelemetry-instrumentation-annotations-1.32.0.jar;%APP_HOME%\lib\opentelemetry-api-1.32.0.jar;%APP_HOME%\lib\transaction-datasource-spi-0.7.0.jar;%APP_HOME%\lib\jwt-spi-0.7.0.jar;%APP_HOME%\lib\runtime-metamodel-0.7.0.jar;%APP_HOME%\lib\policy-evaluator-lib-0.7.0.jar;%APP_HOME%\lib\policy-model-0.7.0.jar;%APP_HOME%\lib\checker-qual-3.42.0.jar;%APP_HOME%\lib\commons-pool2-2.12.0.jar;%APP_HOME%\lib\websocket-jakarta-server-11.0.21.jar;%APP_HOME%\lib\swagger-integration-jakarta-2.2.21.jar;%APP_HOME%\lib\swagger-core-jakarta-2.2.21.jar;%APP_HOME%\lib\junit-jupiter-1.19.8.jar;%APP_HOME%\lib\testcontainers-1.19.8.jar;%APP_HOME%\lib\jetty-annotations-11.0.21.jar;%APP_HOME%\lib\websocket-servlet-11.0.21.jar;%APP_HOME%\lib\docker-java-api-3.3.6.jar;%APP_HOME%\lib\docker-java-transport-zerodep-3.3.6.jar;%APP_HOME%\lib\jetty-plus-11.0.21.jar;%APP_HOME%\lib\jetty-webapp-11.0.21.jar;%APP_HOME%\lib\websocket-jakarta-client-11.0.21.jar;%APP_HOME%\lib\websocket-jakarta-common-11.0.21.jar;%APP_HOME%\lib\websocket-core-client-11.0.21.jar;%APP_HOME%\lib\jetty-client-11.0.21.jar;%APP_HOME%\lib\jetty-servlet-11.0.21.jar;%APP_HOME%\lib\jetty-jndi-11.0.21.jar;%APP_HOME%\lib\jetty-xml-11.0.21.jar;%APP_HOME%\lib\jetty-alpn-client-11.0.21.jar;%APP_HOME%\lib\websocket-core-server-11.0.21.jar;%APP_HOME%\lib\websocket-core-common-11.0.21.jar;%APP_HOME%\lib\jetty-security-11.0.21.jar;%APP_HOME%\lib\jetty-server-11.0.21.jar;%APP_HOME%\lib\jetty-http-11.0.21.jar;%APP_HOME%\lib\jetty-io-11.0.21.jar;%APP_HOME%\lib\jetty-util-11.0.21.jar;%APP_HOME%\lib\slf4j-api-2.0.13.jar;%APP_HOME%\lib\jackson-datatype-jakarta-jsonp-2.17.1.jar;%APP_HOME%\lib\jackson-datatype-jsr310-2.17.1.jar;%APP_HOME%\lib\jackson-dataformat-toml-2.17.1.jar;%APP_HOME%\lib\jackson-jakarta-rs-json-provider-2.17.1.jar;%APP_HOME%\lib\jackson-module-jakarta-xmlbind-annotations-2.17.1.jar;%APP_HOME%\lib\jackson-jakarta-rs-base-2.17.1.jar;%APP_HOME%\lib\jackson-databind-2.17.1.jar;%APP_HOME%\lib\swagger-models-jakarta-2.2.21.jar;%APP_HOME%\lib\jackson-annotations-2.17.1.jar;%APP_HOME%\lib\jackson-core-2.17.1.jar;%APP_HOME%\lib\jackson-dataformat-yaml-2.17.1.jar;%APP_HOME%\lib\snakeyaml-2.2.jar;%APP_HOME%\lib\nimbus-jose-jwt-9.39.1.jar;%APP_HOME%\lib\bcpkix-jdk18on-1.78.1.jar;%APP_HOME%\lib\okhttp-dnsoverhttps-4.12.0.jar;%APP_HOME%\lib\okhttp-4.12.0.jar;%APP_HOME%\lib\classgraph-4.8.165.jar;%APP_HOME%\lib\javassist-3.30.2-GA.jar;%APP_HOME%\lib\swagger-annotations-jakarta-2.2.22.jar;%APP_HOME%\lib\jetty-jakarta-servlet-api-5.0.2.jar;%APP_HOME%\lib\iron-verifiable-credentials-0.14.0.jar;%APP_HOME%\lib\jakarta.json-2.0.1.jar;%APP_HOME%\lib\rdf-urdna-1.1.jar;%APP_HOME%\lib\titanium-json-ld-1.4.0.jar;%APP_HOME%\lib\tink-1.13.0.jar;%APP_HOME%\lib\opentelemetry-context-1.32.0.jar;%APP_HOME%\lib\duct-tape-1.0.8.jar;%APP_HOME%\lib\okio-jvm-3.6.0.jar;%APP_HOME%\lib\kotlin-stdlib-jdk8-1.9.10.jar;%APP_HOME%\lib\kotlin-stdlib-jdk7-1.9.10.jar;%APP_HOME%\lib\kotlin-stdlib-1.9.10.jar;%APP_HOME%\lib\annotations-24.1.0.jar;%APP_HOME%\lib\gson-2.10.1.jar;%APP_HOME%\lib\mockito-core-5.2.0.jar;%APP_HOME%\lib\assertj-core-3.25.3.jar;%APP_HOME%\lib\junit-pioneer-2.2.0.jar;%APP_HOME%\lib\junit-platform-launcher-1.10.2.jar;%APP_HOME%\lib\junit-platform-engine-1.10.2.jar;%APP_HOME%\lib\junit-platform-commons-1.10.2.jar;%APP_HOME%\lib\junit-jupiter-params-5.10.2.jar;%APP_HOME%\lib\junit-jupiter-engine-5.10.2.jar;%APP_HOME%\lib\junit-jupiter-api-5.10.2.jar;%APP_HOME%\lib\bcutil-jdk18on-1.78.1.jar;%APP_HOME%\lib\bcprov-jdk18on-1.78.1.jar;%APP_HOME%\lib\jakarta.json-api-2.1.3.jar;%APP_HOME%\lib\jsr305-3.0.2.jar;%APP_HOME%\lib\error_prone_annotations-2.22.0.jar;%APP_HOME%\lib\protobuf-java-3.25.1.jar;%APP_HOME%\lib\byte-buddy-1.14.11.jar;%APP_HOME%\lib\byte-buddy-agent-1.14.1.jar;%APP_HOME%\lib\objenesis-3.3.jar;%APP_HOME%\lib\opentest4j-1.3.0.jar;%APP_HOME%\lib\jakarta.annotation-api-2.1.1.jar;%APP_HOME%\lib\jakarta.inject-api-2.0.1.jar;%APP_HOME%\lib\jakarta.validation-api-3.0.2.jar;%APP_HOME%\lib\osgi-resource-locator-1.0.3.jar;%APP_HOME%\lib\jakarta.xml.bind-api-4.0.2.jar;%APP_HOME%\lib\mimepull-1.9.15.jar;%APP_HOME%\lib\hk2-locator-3.0.6.jar;%APP_HOME%\lib\jetty-jakarta-websocket-api-2.0.0.jar;%APP_HOME%\lib\commons-lang3-3.14.0.jar;%APP_HOME%\lib\junit-4.13.2.jar;%APP_HOME%\lib\commons-compress-1.24.0.jar;%APP_HOME%\lib\jakarta.activation-api-2.1.3.jar;%APP_HOME%\lib\hk2-api-3.0.6.jar;%APP_HOME%\lib\aopalliance-repackaged-3.0.6.jar;%APP_HOME%\lib\hk2-utils-3.0.6.jar;%APP_HOME%\lib\asm-commons-9.7.jar;%APP_HOME%\lib\asm-tree-9.7.jar;%APP_HOME%\lib\asm-9.7.jar;%APP_HOME%\lib\kotlin-stdlib-common-1.9.10.jar;%APP_HOME%\lib\copper-multicodec-0.1.1.jar;%APP_HOME%\lib\copper-multibase-0.5.0.jar;%APP_HOME%\lib\carbon-did-0.3.0.jar;%APP_HOME%\lib\hamcrest-core-1.3.jar;%APP_HOME%\lib\docker-java-transport-3.3.6.jar;%APP_HOME%\lib\jna-5.13.0.jar;%APP_HOME%\lib\jakarta.transaction-api-2.0.0.jar


@rem Execute launcher
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %LAUNCHER_OPTS%  -classpath "%CLASSPATH%" org.eclipse.edc.boot.system.runtime.BaseRuntime %*

:end
@rem End local scope for the variables with windows NT shell
if %ERRORLEVEL% equ 0 goto mainEnd

:fail
rem Set variable LAUNCHER_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% equ 0 set EXIT_CODE=1
if not ""=="%LAUNCHER_EXIT_CONSOLE%" exit %EXIT_CODE%
exit /b %EXIT_CODE%

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
