import { GET_BUSINESS_ENTITY } from './action';

function transactionWorkflow(state = {}, action) {
  switch (action.type) {
    case GET_BUSINESS_ENTITY:
      return {
        ...state,
        businessEntity: {
          "Customer": { entityType: "Customer", customerId: "customerId" },
          "Payment Mode": { entityType: "Payment Mode", paymentModeId: "paymentModeId" },
          "Merchant": { entityType: "Merchant", merchantId: "merchantId" },
          "Issuer": { entityType: "Issuer", entityTypeId: "entityTypeId" },
          "Network Provider": { entityType: "Network Provider", networkProviderId: "networkProviderId" }
        }
      };
    default:
      return state;
  }
}

export default transactionWorkflow;