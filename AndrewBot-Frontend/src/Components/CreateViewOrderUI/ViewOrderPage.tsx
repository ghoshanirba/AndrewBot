import React, { useEffect, useLayoutEffect, useState } from "react";
import axios from "axios";
import "./ViewOrderPage.css";
import "bootstrap";
import bootstrap, { Tooltip } from "bootstrap";



// interface orderDetails {
//   orderID: number;
//   userID: String;
//   items: {
//     productID: number;
//     productName: String;
//     productBrand: String;
//     productWeight: String;
//     unitPriceMRP: number;
//     productQty: number;
//     discountPercentage: number;
//     totalPriceMRP: number;
//     totalDiscount: number;
//     netPrice: number;
//   }[];
//   orderConfirmedByUser: String;
//   orderCreatedDate: String;
//   orderFulfilled: String;
//   estimatedOrderFulfillmentDate: String;
//   orderFulfillmentDate: String;
//   totalAmountMRP: number;
//   totalDiscountAmount: number;
//   netTotalAmount: number;
//   billingAddress: Address;
//   shippingAdress: Address;
//   paymentMethod: String;
//   rowUpdateUserID: String;
//   rowUpdateTimestamp: String;
// }

interface orderDetails {
  orderID: number;
  userID: string;
  items: Products[];
  orderConfirmedByUser: string;
  orderCreatedDate: string;
  orderFulfilled: string;
  orderFulfillmentDate: string;
  totalAmountMRP: number;
  totalDiscountAmount: number;
  netTotalAmount: number;
  billingAddress: Address;
  shippingAddress: Address;
  paymentMethod: string;
  estimatedOrderFulfillmentDate: string;
}

interface Products {
  id: number;
  name: string;
  weight: string;
  magnitude: number;
  magnitude_unit: string;
  pricing: Pricing;
  brand: Brand;
  category: Category;
  keep_selected: string;
  quantity: number;
  totalMRP: number;
  netSellingPrice: number;
  totalDiscount: number;
}

interface Pricing {
  mrp: number;
  selling_price: number;
  discount: string;
}

interface Brand {
  name: string;
}

interface Category {
  tlc_name: string;
  mlc_name: string;
  ilc_name: string;
}

interface Address {
  houseNumber: string;
  buildingName: string;
  street: string;
  addressLine1: string;
  addressLine2: string;
  addressLine3: string;
  city: string;
  state: string;
  pincode: number;
  landMark: string;
  country: string;
}

// Get current date function
const getCurrentDate = () => {
  const today = new Date();
  const formatDate = today.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  });
  // console.log("formatDate:", formatDate)
  return formatDate
};

//*Function to extract date in DD-MM-YYYY format from Timestamp.
const formatDate = (timestamp: String): string => {
  console.log("Timestamp received: ", timestamp);
  const date = new Date(timestamp.toString());
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  // console.log("Date returned: ", day, "-", month, "-", year);
  return `${day}-${month}-${year}`;
};
//*

export default function ViewOrderPage() {
  const [orderID, setOrderID] = useState<number | null>(null);
  const [orderDetails, setOrderDetails] = useState<orderDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState<string>('');
  const API_URL = "http://127.0.0.1:5000";

  //1st useEffect() hook to retrieve the orderID from localStorage.
  useEffect(() => {
    const storedOrderID = localStorage.getItem("orderID");

    if (storedOrderID) {
      const cleanedOrderID = parseInt(storedOrderID.replace(/"/g, ""));

      // Remove the orderID from localStorage after retrieving it.
      localStorage.removeItem("orderID");

      if (isNaN(cleanedOrderID)) {
        console.error("Stored order ID is not a valid number.");
      } else {
        setOrderID(cleanedOrderID);
      }
    }
  }, []); // Empty dependency array means this runs once on unmount

  //2nd useEffect() hook to call API viewOrder to fetch order details using orderID.
  useEffect(() => {
    // Fetch order details using axios
    const fetchOrder = async (orderID: number) => {
      try {
        const response = await axios.get(`${API_URL}/orders/view`, {
          params: { orderID }, // Pass orderID as a query parameter
        });

        setOrderDetails(response.data);
      } catch (error) {
        setError("Error fetching order details");
        console.error("Error fetching order details:", error);
      } finally {
        setLoading(false);
      }
    };

    // Get the current date
    setCurrentDate(getCurrentDate());

    if (orderID !== null) {
      fetchOrder(orderID);
    }
  }, [orderID]); // Dependency array includes orderID to trigger this effect when orderID changes

  //Debug Statements
  // useEffect(() => {
  //   if (orderDetails) {
  //     console.log("orderID: ", orderDetails?.orderID);
  //     console.log("userID: ", orderDetails?.userID);
  //     console.log("orderConfirmedByUser: ", orderDetails?.orderConfirmedByUser);
  //     console.log("orderCreatedDate: ", orderDetails?.orderCreatedDate);
  //     console.log("orderFulfilled: ", orderDetails?.orderFulfilled);
  //     console.log(
  //       "estimatedOrderFulfillmentDate: ",
  //       orderDetails?.estimatedOrderFulfillmentDate
  //     );
  //     console.log("orderFulfillmentDate: ", orderDetails?.orderFulfillmentDate);
  //     console.log("totalAmountMRP: ", orderDetails?.totalAmountMRP);
  //     console.log("totalDiscountAmount: ", orderDetails?.totalDiscountAmount);
  //     console.log("netTotalAmount: ", orderDetails?.netTotalAmount);
  //     console.log("billingAddress: ", orderDetails?.billingAddress);
  //     console.log("shippingAddress houseNumber: ", orderDetails?.shippingAdress.houseNumber);
  //     console.log("shippingAddress buildingName: ", orderDetails?.shippingAdress.buildingName);
  //     console.log("shippingAddress street: ", orderDetails?.shippingAdress.street);
  //     console.log("shippingAddress addressLine1: ", orderDetails?.shippingAdress.addressLine1);
  //     console.log("shippingAddress addressLine2: ", orderDetails?.shippingAdress.addressLine2);
  //     console.log("shippingAddress addressLine3: ", orderDetails?.shippingAdress.addressLine3);
  //     console.log("shippingAddress city: ", orderDetails?.shippingAdress.city);
  //     console.log("shippingAddress state: ", orderDetails?.shippingAdress.state);
  //     console.log("shippingAddress pincode: ", orderDetails?.shippingAdress.pincode);
  //     console.log("shippingAddress landMark: ", orderDetails?.shippingAdress.landMark);
  //     console.log("shippingAddress country: ", orderDetails?.shippingAdress.country);
  //     console.log("paymentMethod: ", orderDetails?.paymentMethod);
  //     console.log("rowUpdateUserID: ", orderDetails?.rowUpdateUserID);
  //     console.log("rowUpdateTimestamp: ", orderDetails?.rowUpdateTimestamp);
  //   }
  // }, [orderDetails]);
  //

  // useEffect hook to Initialize tooltips
  useEffect(() => {
    const initializeTooltips = () => {
      const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
      );
      console.log("tooltipTriggerList:", tooltipTriggerList);

      tooltipTriggerList.forEach((tooltipTriggerEl) => {
        new Tooltip(tooltipTriggerEl, {
          customClass: "custom-tooltip",
        });
      });
    };

    setTimeout(initializeTooltips, 500); // Adding a delay of 500ms, otherwise AndreBot window is not getting rendered
  }, [orderDetails]);
  //

  document.title = "AndrewBot - View Order";

  function getShippingAddressTooltip(): string | undefined {
    if (!orderDetails) return "";

    const addressLines = [
      orderDetails.shippingAddress.houseNumber,
      orderDetails.shippingAddress.buildingName,
      orderDetails.shippingAddress.street,
      orderDetails.shippingAddress.addressLine1,
      orderDetails.shippingAddress.addressLine2,
      orderDetails.shippingAddress.addressLine3,
      `${orderDetails.shippingAddress.city}, ${orderDetails.shippingAddress.state}`,
      `PIN - ${orderDetails.shippingAddress.pincode}`,
      orderDetails.shippingAddress.landMark,
      orderDetails.shippingAddress.country,
    ]
      .filter((line) => line) // Remove empty lines
      .join(",");

    return addressLines;
  }

  return (
    <>
      <nav className="navbar" style={{ backgroundColor: "#e3f2fd" }}>
        <div className="container-fluid">
          <div className="row w-100">
            <div className="col-6">
              <span className="navbar-brand mb-0 h1">
                AndrewBot - View Order
              </span>
            </div>
            <div className="col-6 text-end pe-5">
              <span className="navbar-text font-monospace fw-semibold">
                User ID: {orderDetails?.userID}
                <br />
                Date: {currentDate}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        <p className="fs-5 fw-semibold text-center text-decoration-underline pt-3">
          Here You Can View Your Order Details
        </p>

        <p className="fs-5 fw-semibold text-success">
          Order ID: {orderDetails?.orderID}
        </p>

        <div className="d-flex pb-3">
          <div className="fs-6 flex-grow-1">
            Date Ordered:{" "}
            {orderDetails?.orderCreatedDate
              ? formatDate(orderDetails.orderCreatedDate)
              : ""}
            ,{" "}
            {orderDetails?.orderFulfilled === "Y"
              ? `Date Delivered: ${formatDate(
                  orderDetails.orderFulfillmentDate
                )}`
              : `Order Not Yet Delivered, Estimated Date Of Delivery: ${
                  orderDetails?.estimatedOrderFulfillmentDate
                    ? formatDate(orderDetails.estimatedOrderFulfillmentDate)
                    : ""
                }`}
          </div>

          <div className="text-end">
            <a
              href="#"
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              title={getShippingAddressTooltip()}
              data-bs-custom-class="custom-tooltip"
              style={{ textDecoration: "none" }}
            >
              Shipped Address
            </a>
          </div>
        </div>

        <div className="table-responsive">
          <table className="table table-secondary table-striped table-bordered table-sm w-auto text-xsmall">
            <thead>
              <tr className="table-secondary">
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  #
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Product Name
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Brand
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Weight
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Quantity
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Unit Price(MRP)
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Total Price(MRP)
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Discount Per Unit
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Total Discount
                </th>
                <th className="table-header-font" scope="col" style={{ textAlign: "center", verticalAlign: "middle" }}>
                  Net Price
                </th>
              </tr>
            </thead>
            <tbody>
              {orderDetails?.items.map((item, index) => (
                <tr className="table table-striped" key={index}>
                  <th scope="row">{index + 1}</th>
                  <td className="table-data-font">{item.name}</td>
                  <td className="table-data-font">{item.brand.name}</td>
                  <td className="table-data-font">{item.weight}</td>
                  <td className="table-data-font">{item.quantity}</td>
                  <td className="table-data-font">
                    Rs. {item.pricing.mrp.toFixed(2)}
                  </td>
                  <td className="table-data-font">
                    Rs. {item.totalMRP.toFixed(2)}
                  </td>
                  <td className="table-data-font">
                    {item.pricing.discount}
                  </td>
                  <td className="table-data-font">
                    Rs. {item.totalDiscount.toFixed(2)}
                  </td>
                  <td className="table-data-font">
                    Rs. {item.netSellingPrice.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="row justify-content-end">
          <div className="col-4">
            <div className="card p-3">
              <h5 className="card-title text-decoration-underline">
                Order Summary
              </h5>
              <p className="card-text">
                Total Price MRP: Rs. {orderDetails?.totalAmountMRP.toFixed(2)}
              </p>
              <p className="card-text">
                Total Discount: Rs.{" "}
                {orderDetails?.totalDiscountAmount.toFixed(2)}
              </p>
              <p className="card-text text-success fw-bold">
                Net Amount Paid: Rs. {orderDetails?.netTotalAmount.toFixed(2)}
              </p>
              <p
                className="fst-italic"
                style={{
                  marginBottom: "0",
                  fontSize: "x-small",
                  textAlign: "end",
                  color: "blue",
                }}
              >
                *Mode Of Payment: {orderDetails?.paymentMethod}
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
