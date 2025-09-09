'use client';

import { useState } from 'react';
import { ApiClient } from '@/lib/api';

const PLANS = [
  {
    code: 'starter' as const,
    name: 'Starter',
    price: '$149',
    description: 'Basic features, 100 conversations',
    features: [
      'SMS & basic messaging',
      'Auto-quotes from photos',
      'Basic booking system',
      '100 conversations/month',
      '14-day free trial'
    ]
  },
  {
    code: 'pro' as const,
    name: 'Pro',
    price: '$299',
    description: 'Advanced features, 500 conversations',
    features: [
      'Everything in Starter',
      'Facebook & Instagram messaging',
      'Advanced quoting with multipliers',
      'Google Calendar sync',
      '500 conversations/month',
      'Priority support'
    ]
  },
  {
    code: 'growth' as const,
    name: 'Growth',
    price: '$499',
    description: 'All features, unlimited conversations',
    features: [
      'Everything in Pro',
      'Unlimited conversations',
      'Advanced analytics',
      'Custom integrations',
      'Dedicated support',
      'White-label options'
    ]
  }
];

export default function BillingPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubscribe = async (planCode: 'starter' | 'pro' | 'growth') => {
    setLoading(planCode);
    setError(null);

    try {
      const result = await ApiClient.createCheckoutSession({
        plan_code: planCode,
        tenant_id: 'demo-tenant', // TODO: Get from auth context
        customer_email: 'demo@example.com', // TODO: Get from auth context
        success_url: `${window.location.origin}/billing/success`,
        cancel_url: `${window.location.origin}/billing`,
        trial_days: 14
      });

      // Redirect to Stripe checkout
      window.location.href = result.checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create checkout session');
    } finally {
      setLoading(null);
    }
  };

  const handleManageSubscription = async () => {
    setLoading('portal');
    setError(null);

    try {
      const result = await ApiClient.createPortalSession({
        customer_id: 'cus_demo', // TODO: Get from user context
        return_url: window.location.href
      });

      // Redirect to Stripe customer portal
      window.location.href = result.portal_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open customer portal');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className=\"min-h-screen bg-gray-50 py-12\">
      <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
        <div className=\"text-center mb-12\">
          <h1 className=\"text-4xl font-bold text-gray-900 mb-4\">
            Choose Your Plan
          </h1>
          <p className=\"text-xl text-gray-600\">
            Start your 14-day free trial today. No credit card required.
          </p>
        </div>

        {error && (
          <div className=\"mb-8 p-4 bg-red-50 border border-red-200 rounded-md\">
            <p className=\"text-red-700\">{error}</p>
          </div>
        )}

        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-8 mb-12\">
          {PLANS.map((plan) => (
            <div
              key={plan.code}
              className=\"bg-white rounded-lg shadow-md p-8 relative hover:shadow-lg transition-shadow\"
            >
              <div className=\"text-center mb-6\">
                <h3 className=\"text-2xl font-bold text-gray-900 mb-2\">{plan.name}</h3>
                <div className=\"text-4xl font-bold text-indigo-600 mb-2\">{plan.price}</div>
                <p className=\"text-gray-600\">{plan.description}</p>
              </div>

              <ul className=\"space-y-3 mb-8\">
                {plan.features.map((feature, index) => (
                  <li key={index} className=\"flex items-start\">
                    <svg
                      className=\"w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0\"
                      fill=\"currentColor\"
                      viewBox=\"0 0 20 20\"
                    >
                      <path
                        fillRule=\"evenodd\"
                        d=\"M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z\"
                        clipRule=\"evenodd\"
                      />
                    </svg>
                    <span className=\"text-gray-700\">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan.code)}
                disabled={loading === plan.code}
                className=\"w-full bg-indigo-600 text-white py-3 px-4 rounded-md font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors\"
              >
                {loading === plan.code ? 'Loading...' : 'Start Free Trial'}
              </button>
            </div>
          ))}
        </div>

        <div className=\"text-center\">
          <button
            onClick={handleManageSubscription}
            disabled={loading === 'portal'}
            className=\"inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 bg-white rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors\"
          >
            {loading === 'portal' ? 'Loading...' : 'Manage Existing Subscription'}
          </button>
        </div>
      </div>
    </div>
  );
}