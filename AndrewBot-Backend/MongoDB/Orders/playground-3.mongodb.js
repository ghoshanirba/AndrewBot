/* global use, db */
// MongoDB Playground
// To disable this template go to Settings | MongoDB | Use Default Template For Playground.
// Make sure you are connected to enable completions and to be able to run a playground.
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.
// The result of the last command run in a playground is shown on the results panel.
// By default the first 20 documents will be returned with a cursor.
// Use 'console.log()' to print to the debug output.
// For more documentation on playgrounds please refer to
// https://www.mongodb.com/docs/mongodb-vscode/playgrounds/

// Select the database to use.
use('AndrewBot');

const items = [
  {
    productID: 1,
    productName: "wheat",
    productBrand: "aashirvad",
    productWeight: "5kg",
    unitPriceMRP: 250.00,
    productQty: 1,
    discountPercentage: 2,
    totalPriceMRP: 0.00,
    totalDiscount: 0.00,
    netPrice: 0.00
  },
  {
    productID: 2,
    productName: "rice",
    productBrand: "india gate",
    productWeight: "2kg",
    unitPriceMRP: 300.00,
    productQty: 2,
    discountPercentage: 3,
    totalPriceMRP: 0.00,
    totalDiscount: 0.00,
    netPrice: 0.00
  },
  {
    productID: 3,
    productName: "turmeric",
    productBrand: "sunrise",
    productWeight: "200gm",
    unitPriceMRP: 120.00,
    productQty: 3,
    discountPercentage: 3,
    totalPriceMRP: 0.00,
    totalDiscount: 0.00,
    netPrice: 0.00
  }
];

function calculatePrices(items) {
  let totalAmountMRP = 0.00;
  let totalDiscountAmount = 0.00;

  items.forEach(item => {
    item.totalPriceMRP = parseFloat((item.unitPriceMRP * item.productQty).toFixed(2));
    item.totalDiscount = parseFloat((item.totalPriceMRP * (item.discountPercentage / 100)).toFixed(2));
    item.netPrice      = parseFloat((item.totalPriceMRP - item.totalDiscount).toFixed(2));
    // item.totalPriceMRP  = (item.unitPriceMRP * item.productQty);
    // item.totalDiscount  = (item.totalPriceMRP * (item.discountPercentage / 100));
    // item.netPrice       = (item.totalPriceMRP - item.totalDiscount);
    totalAmountMRP      = parseFloat((totalAmountMRP + item.totalPriceMRP).toFixed(2));
    totalDiscountAmount = parseFloat((totalDiscountAmount + item.totalDiscount).toFixed(2));
  });

  return {
    items,
    totalAmountMRP,
    totalDiscountAmount,
    netTotalAmount: parseFloat((totalAmountMRP - totalDiscountAmount).toFixed(2))
  };
}

const {items: updatedItems, totalAmountMRP, totalDiscountAmount, netTotalAmount} = calculatePrices(items);

const billingAddress = {
  houseNumber: 102,
  buildingName: "ABC Building",
  street: "XYZ Street",
  addressLine1: "Address Line 1",
  addressLine2: "Address Line 2",
  addressLine3: "Address Line 3",
  city: "EFG city",
  state: "test state",
  pincode: 12345,
  landMark: "Opposite GHI building",
  country: "test country"
}

const shippingAdress = {
  houseNumber: 102,
  buildingName: "ABC Building",
  street: "XYZ Street",
  addressLine1: "Address Line 1",
  addressLine2: "Address Line 2",
  addressLine3: "Address Line 3",
  city: "EFG city",
  state: "test state",
  pincode: 12345,
  landMark: "Opposite GHI building",
  country: "test country"
}

// Insert a few documents into the sales collection.
db.getCollection('Orders').insertOne(
    {
        orderID: 100003,
        userID: "ghoshanirban",
        items: updatedItems,
        orderConfirmedByUser: "Y",
        orderCreatedDate: new Date().toISOString(),
        orderFulfilled: "N",
        estimatedOrderFulfillmentDate: new Date().toISOString(),
        orderFulfillmentDate: new Date().toISOString(),
        totalAmountMRP: totalAmountMRP,
        totalDiscountAmount: totalDiscountAmount,
        netTotalAmount: netTotalAmount,
        billingAddress: billingAddress,
        shippingAdress: shippingAdress,
        paymentMethod: "credit card",
        rowUpdateUserID: "ghoshanirban",
        rowUpdateTimestamp: new Date().toISOString()
        
    }
);

