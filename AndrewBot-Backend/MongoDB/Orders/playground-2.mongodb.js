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
    unitPriceMRP: Double((250.00).toFixed(2)),
    productQty: 1,
    discountPercentage: 2,
    totalPriceMRP: Double((0.00).toFixed(2)),
    totalDiscount: Double((0.00).toFixed(2)),
    netPrice: Double((0.00).toFixed(2))
  },
  {
    productID: 2,
    productName: "rice",
    productBrand: "india gate",
    productWeight: "2kg",
    unitPriceMRP: Double((300.00).toFixed(2)),
    productQty: 2,
    discountPercentage: 3,
    totalPriceMRP: Double((0.00).toFixed(2)),
    totalDiscount: Double((0.00).toFixed(2)),
    netPrice: Double((0.00).toFixed(2))
  },
  {
    productID: 3,
    productName: "turmeric",
    productBrand: "sunrise",
    productWeight: "200gm",
    unitPriceMRP: Double((120.00).toFixed(2)),
    productQty: 3,
    discountPercentage: 3,
    totalPriceMRP: Double((0.00).toFixed(2)),
    totalDiscount: Double((0.00).toFixed(2)),
    netPrice: Double((0.00).toFixed(2))
  }
];

function calculatePrices(items) {
  let totalAmountMRP = Double(0.00);
  let totalDiscountAmount = Double(0.00);

  items.forEach(item => {
    // item.totalPriceMRP = parseFloat((item.unitPriceMRP * item.productQty).toFixed(2));
    // item.totalDiscount = parseFloat((item.totalPriceMRP * (item.discountPercentage / 100)).toFixed(2));
    // item.netPrice = parseFloat((item.totalPriceMRP - item.totalDiscount).toFixed(2));
    item.totalPriceMRP  = parseFloat((item.unitPriceMRP * item.productQty).toFixed(2));
    item.totalDiscount  = parseFloat((item.totalPriceMRP * (item.discountPercentage / 100)).toFixed(2));
    item.netPrice       = parseFloat((item.totalPriceMRP - item.totalDiscount).toFixed(2));
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

// Insert a few documents into the sales collection.
db.getCollection('Orders').insertOne(
    {
        orderID: 100001,
        userID: "ghoshanirban",
        items: updatedItems,
        orderConfirmedByUser: "Y",
        orderCreatedDate: new Date().toISOString(),
        orderFulfilled: "N",
        estimatedOrderFulfulfillmentDate: new Date().toISOString(),
        OrderFulfillmentDate: new Date().toISOString(),
        totalAmountMRP: parseFloat(totalAmountMRP.toFixed(2)),
        totalDiscountAmount: parseFloat(totalDiscountAmount.toFixed(2)),
        netTotalAmount: parseFloat(netTotalAmount.toFixed(2)),
        rowUpdateUserID: "ghoshanirban",
        rowUpdateTimestamp: new Date().toISOString()
        
      }
);

