import { useConfig } from "../config/ConfigContext";

export interface IssueVcRequest {
  connector_did: string;
  connector_dsp_url: string;
  identity_hub_identity_url: string;
  identity_hub_api_key: string;
}

export function useRegistrationApiService() {
  const { apiBaseUrl } = useConfig();

  async function issueVc(
    data: IssueVcRequest
  ): Promise<any> {

    const path = `${apiBaseUrl}/v1/verifiable-credentials/issue`

    const response = await fetch(path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`VC issuance failed: ${errorText}`);
    }

    return response.json();
  }

  return { issueVc };
}
