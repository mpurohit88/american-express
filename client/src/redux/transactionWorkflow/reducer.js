import { GET_BUSINESS_ENTITY } from './action';

function transactionWorkflow(state = {}, action) {
  switch (action.type) {
    case GET_BUSINESS_ENTITY:
      return { ...state, businessEntity: ["Customer", "Payment Mode", "Merchant"] };
    default:
      return state;
  }
}

export default transactionWorkflow;