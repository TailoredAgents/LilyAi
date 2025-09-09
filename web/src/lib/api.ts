const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CheckoutRequest {
  plan_code: 'starter' | 'pro' | 'growth';
  tenant_id: string;
  customer_email: string;
  success_url: string;
  cancel_url: string;
  trial_days?: number;
}

export interface PortalRequest {
  customer_id: string;
  return_url: string;
}

export class ApiClient {
  private static async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  static async createCheckoutSession(request: CheckoutRequest) {
    return this.request('/api/v1/billing/checkout', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async createPortalSession(request: PortalRequest) {
    return this.request('/api/v1/billing/portal', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async getHealth() {
    return this.request('/health');
  }
}