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
@rem  connector startup script for Windows
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

@rem Add default JVM options here. You can also use JAVA_OPTS and CONNECTOR_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\lib\connector-0.2.0.jar;%APP_HOME%\lib\control-plane-core-0.2.1.jar;%APP_HOME%\lib\dsp-0.2.1.jar;%APP_HOME%\lib\configuration-filesystem-0.2.1.jar;%APP_HOME%\lib\vault-filesystem-0.2.1.jar;%APP_HOME%\lib\iam-mock-0.2.1.jar;%APP_HOME%\lib\management-api-0.2.1.jar;%APP_HOME%\lib\transfer-data-plane-0.2.1.jar;%APP_HOME%\lib\transfer-pull-http-receiver-0.2.1.jar;%APP_HOME%\lib\api-observability-0.2.1.jar;%APP_HOME%\lib\data-plane-selector-api-0.2.1.jar;%APP_HOME%\lib\data-plane-selector-core-0.2.1.jar;%APP_HOME%\lib\data-plane-selector-client-0.2.1.jar;%APP_HOME%\lib\data-plane-api-0.2.1.jar;%APP_HOME%\lib\data-plane-core-0.2.1.jar;%APP_HOME%\lib\data-plane-http-0.2.1.jar;%APP_HOME%\lib\connector-core-0.2.1.jar;%APP_HOME%\lib\boot-0.2.1.jar;%APP_HOME%\lib\policy-engine-0.2.1.jar;%APP_HOME%\lib\catalog-core-0.2.1.jar;%APP_HOME%\lib\contract-core-0.2.1.jar;%APP_HOME%\lib\transfer-core-0.2.1.jar;%APP_HOME%\lib\control-plane-aggregate-services-0.2.1.jar;%APP_HOME%\lib\asset-api-0.2.1.jar;%APP_HOME%\lib\catalog-api-0.2.1.jar;%APP_HOME%\lib\contract-agreement-api-0.2.1.jar;%APP_HOME%\lib\contract-definition-api-0.2.1.jar;%APP_HOME%\lib\contract-negotiation-api-0.2.1.jar;%APP_HOME%\lib\policy-definition-api-0.2.1.jar;%APP_HOME%\lib\transfer-process-api-0.2.1.jar;%APP_HOME%\lib\management-api-configuration-0.2.1.jar;%APP_HOME%\lib\control-api-configuration-0.2.1.jar;%APP_HOME%\lib\api-core-0.2.1.jar;%APP_HOME%\lib\data-plane-client-0.2.1.jar;%APP_HOME%\lib\data-plane-selector-spi-0.2.1.jar;%APP_HOME%\lib\data-plane-framework-0.2.1.jar;%APP_HOME%\lib\data-plane-util-0.2.1.jar;%APP_HOME%\lib\util-0.2.1.jar;%APP_HOME%\lib\dsp-catalog-0.2.1.jar;%APP_HOME%\lib\dsp-catalog-api-0.2.1.jar;%APP_HOME%\lib\dsp-negotiation-0.2.1.jar;%APP_HOME%\lib\dsp-negotiation-api-0.2.1.jar;%APP_HOME%\lib\dsp-transfer-process-0.2.1.jar;%APP_HOME%\lib\dsp-transfer-process-api-0.2.1.jar;%APP_HOME%\lib\dsp-transfer-process-http-dispatcher-0.2.1.jar;%APP_HOME%\lib\control-plane-spi-0.2.1.jar;%APP_HOME%\lib\dsp-api-configuration-0.2.1.jar;%APP_HOME%\lib\dsp-catalog-http-dispatcher-0.2.1.jar;%APP_HOME%\lib\dsp-negotiation-http-dispatcher-0.2.1.jar;%APP_HOME%\lib\dsp-http-core-0.2.1.jar;%APP_HOME%\lib\dsp-catalog-transform-0.2.1.jar;%APP_HOME%\lib\dsp-negotiation-transform-0.2.1.jar;%APP_HOME%\lib\dsp-transfer-process-transform-0.2.1.jar;%APP_HOME%\lib\dsp-http-spi-0.2.1.jar;%APP_HOME%\lib\dsp-spi-0.2.1.jar;%APP_HOME%\lib\json-ld-0.2.1.jar;%APP_HOME%\lib\transform-core-0.2.1.jar;%APP_HOME%\lib\catalog-spi-0.2.1.jar;%APP_HOME%\lib\contract-spi-0.2.1.jar;%APP_HOME%\lib\transfer-spi-0.2.1.jar;%APP_HOME%\lib\http-0.2.1.jar;%APP_HOME%\lib\jersey-core-0.2.1.jar;%APP_HOME%\lib\jersey-providers-0.2.1.jar;%APP_HOME%\lib\auth-spi-0.2.1.jar;%APP_HOME%\lib\jetty-core-0.2.1.jar;%APP_HOME%\lib\web-spi-0.2.1.jar;%APP_HOME%\lib\transfer-data-plane-spi-0.2.1.jar;%APP_HOME%\lib\data-plane-spi-0.2.1.jar;%APP_HOME%\lib\http-spi-0.2.1.jar;%APP_HOME%\lib\aggregate-service-spi-0.2.1.jar;%APP_HOME%\lib\validator-core-0.2.1.jar;%APP_HOME%\lib\json-ld-spi-0.2.1.jar;%APP_HOME%\lib\transform-spi-0.2.1.jar;%APP_HOME%\lib\data-plane-http-spi-0.2.1.jar;%APP_HOME%\lib\policy-engine-spi-0.2.1.jar;%APP_HOME%\lib\transaction-datasource-spi-0.2.1.jar;%APP_HOME%\lib\validator-spi-0.2.1.jar;%APP_HOME%\lib\state-machine-0.2.1.jar;%APP_HOME%\lib\policy-spi-0.2.1.jar;%APP_HOME%\lib\asset-spi-0.2.1.jar;%APP_HOME%\lib\jwt-core-0.2.1.jar;%APP_HOME%\lib\jwt-spi-0.2.1.jar;%APP_HOME%\lib\control-plane-api-client-spi-0.2.1.jar;%APP_HOME%\lib\core-spi-0.2.1.jar;%APP_HOME%\lib\transaction-spi-0.2.1.jar;%APP_HOME%\lib\policy-evaluator-0.2.1.jar;%APP_HOME%\lib\policy-model-0.2.1.jar;%APP_HOME%\lib\runtime-metamodel-0.2.1.jar;%APP_HOME%\lib\okhttp-dnsoverhttps-4.11.0.jar;%APP_HOME%\lib\failsafe-okhttp-3.3.2.jar;%APP_HOME%\lib\okhttp-4.11.0.jar;%APP_HOME%\lib\okio-jvm-3.2.0.jar;%APP_HOME%\lib\kotlin-stdlib-jdk8-1.6.20.jar;%APP_HOME%\lib\kotlin-stdlib-jdk7-1.6.20.jar;%APP_HOME%\lib\kotlin-stdlib-1.6.20.jar;%APP_HOME%\lib\annotations-24.0.1.jar;%APP_HOME%\lib\swagger-jaxrs2-jakarta-2.2.2.jar;%APP_HOME%\lib\swagger-integration-jakarta-2.2.2.jar;%APP_HOME%\lib\swagger-core-jakarta-2.2.2.jar;%APP_HOME%\lib\swagger-models-jakarta-2.2.2.jar;%APP_HOME%\lib\jackson-jakarta-rs-json-provider-2.15.2.jar;%APP_HOME%\lib\jersey-media-json-jackson-3.1.3.jar;%APP_HOME%\lib\jackson-module-jakarta-xmlbind-annotations-2.15.2.jar;%APP_HOME%\lib\jackson-annotations-2.15.2.jar;%APP_HOME%\lib\jackson-datatype-jakarta-jsonp-2.15.2.jar;%APP_HOME%\lib\jackson-jakarta-rs-base-2.15.2.jar;%APP_HOME%\lib\jackson-dataformat-yaml-2.15.2.jar;%APP_HOME%\lib\jackson-datatype-jsr310-2.15.2.jar;%APP_HOME%\lib\jackson-databind-2.15.2.jar;%APP_HOME%\lib\jackson-core-2.15.2.jar;%APP_HOME%\lib\bcpkix-jdk18on-1.76.jar;%APP_HOME%\lib\jersey-container-servlet-3.1.3.jar;%APP_HOME%\lib\jersey-container-servlet-core-3.1.3.jar;%APP_HOME%\lib\jersey-server-3.1.3.jar;%APP_HOME%\lib\jersey-media-multipart-3.1.3.jar;%APP_HOME%\lib\jersey-hk2-3.1.3.jar;%APP_HOME%\lib\jersey-client-3.1.3.jar;%APP_HOME%\lib\jersey-common-3.1.3.jar;%APP_HOME%\lib\jersey-entity-filtering-3.1.3.jar;%APP_HOME%\lib\jakarta.ws.rs-api-3.1.0.jar;%APP_HOME%\lib\nimbus-jose-jwt-9.31.jar;%APP_HOME%\lib\opentelemetry-instrumentation-annotations-1.29.0.jar;%APP_HOME%\lib\opentelemetry-api-1.29.0.jar;%APP_HOME%\lib\websocket-jakarta-server-11.0.15.jar;%APP_HOME%\lib\websocket-servlet-11.0.15.jar;%APP_HOME%\lib\jetty-annotations-11.0.15.jar;%APP_HOME%\lib\websocket-jakarta-client-11.0.15.jar;%APP_HOME%\lib\websocket-jakarta-common-11.0.15.jar;%APP_HOME%\lib\websocket-core-client-11.0.15.jar;%APP_HOME%\lib\jetty-client-11.0.15.jar;%APP_HOME%\lib\jetty-plus-11.0.15.jar;%APP_HOME%\lib\jetty-webapp-11.0.15.jar;%APP_HOME%\lib\jetty-servlet-11.0.15.jar;%APP_HOME%\lib\websocket-core-server-11.0.15.jar;%APP_HOME%\lib\websocket-core-common-11.0.15.jar;%APP_HOME%\lib\jetty-security-11.0.15.jar;%APP_HOME%\lib\jetty-server-11.0.15.jar;%APP_HOME%\lib\jetty-http-11.0.15.jar;%APP_HOME%\lib\jetty-alpn-client-11.0.15.jar;%APP_HOME%\lib\jetty-io-11.0.15.jar;%APP_HOME%\lib\jetty-jndi-11.0.15.jar;%APP_HOME%\lib\jetty-xml-11.0.15.jar;%APP_HOME%\lib\jetty-util-11.0.15.jar;%APP_HOME%\lib\slf4j-api-2.0.7.jar;%APP_HOME%\lib\jakarta.json-2.0.1.jar;%APP_HOME%\lib\failsafe-3.3.2.jar;%APP_HOME%\lib\bcutil-jdk18on-1.76.jar;%APP_HOME%\lib\bcprov-jdk18on-1.76.jar;%APP_HOME%\lib\swagger-annotations-jakarta-2.2.15.jar;%APP_HOME%\lib\classgraph-4.8.138.jar;%APP_HOME%\lib\javassist-3.29.2-GA.jar;%APP_HOME%\lib\jcip-annotations-1.0-1.jar;%APP_HOME%\lib\titanium-json-ld-1.3.2.jar;%APP_HOME%\lib\opentelemetry-context-1.29.0.jar;%APP_HOME%\lib\jakarta.json-api-2.1.1.jar;%APP_HOME%\lib\jetty-jakarta-servlet-api-5.0.2.jar;%APP_HOME%\lib\kotlin-stdlib-common-1.6.20.jar;%APP_HOME%\lib\commons-lang3-3.12.0.jar;%APP_HOME%\lib\jakarta.xml.bind-api-4.0.0.jar;%APP_HOME%\lib\jakarta.validation-api-3.0.2.jar;%APP_HOME%\lib\jakarta.annotation-api-2.1.1.jar;%APP_HOME%\lib\jakarta.inject-api-2.0.1.jar;%APP_HOME%\lib\osgi-resource-locator-1.0.3.jar;%APP_HOME%\lib\mimepull-1.9.15.jar;%APP_HOME%\lib\hk2-locator-3.0.4.jar;%APP_HOME%\lib\jetty-jakarta-websocket-api-2.0.0.jar;%APP_HOME%\lib\snakeyaml-2.0.jar;%APP_HOME%\lib\jakarta.activation-api-2.1.0.jar;%APP_HOME%\lib\hk2-api-3.0.4.jar;%APP_HOME%\lib\aopalliance-repackaged-3.0.4.jar;%APP_HOME%\lib\hk2-utils-3.0.4.jar;%APP_HOME%\lib\asm-commons-9.5.jar;%APP_HOME%\lib\asm-tree-9.5.jar;%APP_HOME%\lib\asm-9.5.jar;%APP_HOME%\lib\jakarta.transaction-api-2.0.0.jar


@rem Execute connector
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %CONNECTOR_OPTS%  -classpath "%CLASSPATH%" org.eclipse.edc.boot.system.runtime.BaseRuntime %*

:end
@rem End local scope for the variables with windows NT shell
if %ERRORLEVEL% equ 0 goto mainEnd

:fail
rem Set variable CONNECTOR_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% equ 0 set EXIT_CODE=1
if not ""=="%CONNECTOR_EXIT_CONSOLE%" exit %EXIT_CODE%
exit /b %EXIT_CODE%

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
