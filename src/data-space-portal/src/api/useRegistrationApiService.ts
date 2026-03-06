import { useConfig } from "../config/ConfigContext";

export interface RegisterParticipantDto {
  connector_did: string;
  connector_dsp_url: string;
  connector_management_url: string;
  connector_api_key: string;
  identity_hub_identity_url: string;
  identity_hub_credentials_url: string;
  identity_hub_api_key: string;
  sts_public_key_pem: string;
  generated_vcs: unknown[];
}

export function useRegistrationApiService() {
  const { apiBaseUrl } = useConfig();

  async function registerParticipant(
    data: RegisterParticipantDto
  ): Promise<any> {

    const path = `${apiBaseUrl}/v1/verifiable-credentials/test`

    const response = await fetch(path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Registration failed: ${errorText}`);
    }

    return response.json();
  }

  return { registerParticipant };
}
