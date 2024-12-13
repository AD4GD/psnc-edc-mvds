/*
 *  Copyright (c) 2024 Amadeus IT Group
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Amadeus IT Group - initial API and implementation
 *
 */

plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.crawler.spi)
    implementation(libs.edc.sql.core)
    implementation(libs.edc.sql.bootstrapper)
    implementation(libs.edc.spi.transaction.datasource)
    implementation(libs.edc.lib.util)
}
