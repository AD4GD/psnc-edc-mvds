/*
 *  Copyright (c) 2024 Bayerische Motoren Werke Aktiengesellschaft (BMW AG)
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Bayerische Motoren Werke Aktiengesellschaft (BMW AG) - initial API and implementation
 *
 */

package org.eclipse.edc.sample.runtime;

import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.security.Vault;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

public class SeedVaultExtension implements ServiceExtension {

    @Inject
    private Vault vault;

    private static final String PUBLIC_KEY = """
            -----BEGIN CERTIFICATE-----
            MIICpTCCAY0CBgGQ2xYEnjANBgkqhkiG9w0BAQsFADAWMRQwEgYDVQQDDAtkYXBz
            LWNsaWVudDAeFw0yNDA3MjIxNTM0MzFaFw0zNDA3MjIxNTM2MTFaMBYxFDASBgNV
            BAMMC2RhcHMtY2xpZW50MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
            uJ+81eNZl6mVLzsXdWI5vSeugFOtrDpkCML2pBkQ+CGuMEQpMHxSXJ1kUuF1lbJl
            OL0N1JsRgRItntspaMoiM+dxDnlwvQDNvcVlB3hV9YuEyCPjeFeeNJoJWT9qxll7
            bcLQfcjFj/Lp9NmC2WoRyVRgBfdtr7+KBY3Pnlat4GzguvzYkQnv3nIkUshB4UFd
            8i0SyP/iLisDgz6Wf0atVMSduWVqA4y1LST2f/JuYETh85odHaPLt9HktmNNsKoo
            ge3LhvkaG1aC1kkwz1uSrgnWJ/UJLn0kUeC+BVsKFgcmnjecDFw8BmFn0gch8EkM
            5rm7RFDL/3G2cmLkEJW77wIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQB5/c8qu2Lb
            YSig5U9UEoDAGZ/0TqLKaEj7I53cqUpMpUYtnxCbFZtDktOJGvg3YNK/Ztv1VGOx
            ADoAfdyDD/EboTGQ+rmXDCZmyL5oPbHLGgMazih/7qu3qfuMN/LBUEiPp5JLXU7x
            A41mTBCraAYJ8ddQCN0b9CMOr7SNHtkja6oT0gEV6c5iwqOFcPpxcf/PufKm3R2H
            jh/z1tHHjNkEo499PGZlpXNNr6VgDIs501cWag0S4ZFkK8SoGsttNB4eAChj0CdT
            mV8lLAwYAXLlWmAJxF7XIE1M9ZTbKwfMspNomYARgpneMUPoigU4CTZfazQzGiHo
            SNCoRTr7sMBT
            -----END CERTIFICATE-----
            """;

    private static final String PRIVATE_KEY = """
            -----BEGIN PRIVATE KEY-----
            MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC4n7zV41mXqZUv
            Oxd1Yjm9J66AU62sOmQIwvakGRD4Ia4wRCkwfFJcnWRS4XWVsmU4vQ3UmxGBEi2e
            2yloyiIz53EOeXC9AM29xWUHeFX1i4TII+N4V540mglZP2rGWXttwtB9yMWP8un0
            2YLZahHJVGAF922vv4oFjc+eVq3gbOC6/NiRCe/eciRSyEHhQV3yLRLI/+IuKwOD
            PpZ/Rq1UxJ25ZWoDjLUtJPZ/8m5gROHzmh0do8u30eS2Y02wqiiB7cuG+RobVoLW
            STDPW5KuCdYn9QkufSRR4L4FWwoWByaeN5wMXDwGYWfSByHwSQzmubtEUMv/cbZy
            YuQQlbvvAgMBAAECggEADfnBkKtaH9ntehrOBsu9tSzoz7wF3JC6+9LOWtOu7imW
            hv7R42K11V7wtjls7j0H3oipIFvwskWPAIR0mQMcHbO6Yi8dMqF58ZCcujkIwMKj
            9YaJ9JUlW7QBWykqywMBDej+YVcuZVwtC6Tfe9fEqunhLvJw8incp9j5S3IiTWev
            lyzagaQCnaFZ2lKZwFUouQ6s+LiUEFnpJIqlvCFj80QYaHa+Q2FiRntNSYKRnEOB
            6QfhcLC4zTH7LjhDoGobucbMdOLNw7pqMiao5vGPAWh3QWY+RUABHBhwMMyyds9U
            5dAuY4Mcx2ey1kMLTri2nTMC7DJkva7FrQj1/2THcQKBgQDh21c5YlmW+YnyRrGh
            LkicnE3Hj8vFhgY2J2KQGJA8QEQYADLu+9nmyTNQpfQz54bUlwS1uI30IExjBEAZ
            OY+M7Qg537zfwpWIZ+VUlxtCnfbF0t8MIxM9szKQCWSJO0OFm0kA0ZwwmkaV8d5X
            Nk620/IESII02rXmsm9CeVUmVwKBgQDRQ6EzTsJKq6FEy7d4Ci8+nXnXgpsEt4XK
            FaOpKr58z8PhZGgO3WcSTmVaQ3ncnYdla1pLcs2f9/pQtvcXvT7TUXoRpMvoRXH6
            jou/CH7BICZunfl4JIeoLPjINjpY1iFn4Uh8zMJnP37dVVrRIySHncPWmu7LJ6YE
            SoXsMJMoKQKBgBi5L/UiJPh33Hfe8TbZoC00lvcPcJjwsOFgslNfvPo7drjB3NF4
            VEQFJk7fu7mq0IGY/nT9/NwKZRI5tuKMAIDGua3MJhrAbCoAZYQ6/krui8Lf8Had
            qE+KvDA0NwMmr5+Cfh1O1LAlUzC6x0H4uekdjlKVtVsfzeWxBqjaK04FAoGAS5Om
            Q3Z9WyRzQPpmD5d2CqIrH/dObzysuBhqnC0Q0NjkgKGXp0606/qeRiQ6fb/y52EH
            IlqbAtw3bjE2Oj+h0gYKFRc0gXWbPYd/1wWFadBnsOmi8I4Y5FchnoVfOzhSpkbJ
            vDDjQRDAi8VI4GFVzxjeYsJf3cU7Ay+7AFtmukkCgYEAwuziHc5Old0nofZR7QIj
            SvkocaPVJoOYfeN8m6AZoIysj9rnxm3oT0VMT5khtRmPBvKmfW5P9e+l2fcx3Qho
            aV3qQgYTCR2/t1tgmXEw2RGlgWPW8iKf9h1kCMEhbYeiaeu5Ees22ELdFSBI8TvL
            fE1XJ9r/oaLP4LvCa/xdF3Q=
            -----END PRIVATE KEY-----
            """;

    @Override
    public void initialize(ServiceExtensionContext context) {
        vault.storeSecret("dapsPublic", PUBLIC_KEY);
        vault.storeSecret("dapsPrivate", PRIVATE_KEY);
    }
}
