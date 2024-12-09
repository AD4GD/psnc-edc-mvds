/*
 *  Copyright (c) 2022 Microsoft Corporation
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Microsoft Corporation - initial API and implementation
 *
 */

plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    implementation(libs.edc.spi.core)
    
    runtimeOnly(project(":core:registration-service"))
    runtimeOnly(project(":core:registration-service-credential-service"))
    runtimeOnly(project(":extensions:registration-service-api"))
    runtimeOnly(libs.edc.ext.identity.did.web)
    runtimeOnly(libs.edc.ext.identity.did.core)
    runtimeOnly(libs.edc.core.connector)
    runtimeOnly(libs.edc.boot)
    runtimeOnly(libs.edc.ext.observability)
    runtimeOnly(libs.edc.ext.json.ld)
    runtimeOnly(libs.edc.core.micrometer)
    runtimeOnly(libs.edc.ext.micrometer.jetty)
    runtimeOnly(libs.edc.ext.micrometer.jersey)
    runtimeOnly(libs.edc.ext.configuration.filesystem)
    runtimeOnly(libs.ih.core.verifier)
    runtimeOnly(libs.ih.ext.verifier.jwt)

    runtimeOnly(project(":extensions:store:sql:participant-store-sql"))

    // register SQL
    implementation(libs.edc.core.spi)
    //implementation(libs.edc.sql.core)

    // Adds Database-Related EDC-Extensions (EDC-SQL-Stores, JDBC-Driver, Pool and Transactions)
    implementation(libs.edc.control.plane.sql)
    implementation(libs.edc.transaction.local)
    implementation(libs.postgresql)
    implementation(libs.flyway.core)

    implementation(libs.edc.sql.pool.apache.commons)

    // JDK Logger
    runtimeOnly(libs.edc.ext.jdklogger)

    // To use FileSystem vault e.g. -DuseFsVault="true".Only for non-production usages.
    val useFsVault: Boolean = System.getProperty("useFsVault", "false").toBoolean()
    if (useFsVault) {
        runtimeOnly(libs.edc.ext.vault.filesystem)
    } else {
        logger.lifecycle("The system property 'useFsVault' was either not specified, or was set to 'false'. The runtime will use the InMemoryVault!")
    }
}

application {
    mainClass.set("org.eclipse.edc.boot.system.runtime.BaseRuntime")
}

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    mergeServiceFiles()
    archiveFileName.set("app.jar")
}

edcBuild {
    publish.set(false)
}
