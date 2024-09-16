import axios from "axios";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

interface APIResponse {
  tabs: Tabs;
}

interface Tabs {
  product_info: ProductInfo;
  total_count_of_all_products: number;
}

interface ProductInfo {
  products: Product[];
}

interface Product {
  id: number;
  name: string;
  weight: string;
  magnitude: number;
  magnitude_unit: string;
  pricing: Pricing;
  brand: Brand;
  category: Category;
  keep_selected: string;
  children?: Product[]; //Optional field as it will be present for only main product.
  total_count_of_one_product_with_children?: number; // Optional field since it's only present in the main product
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


interface APIErrorResponse {
  error : string
}

type orderResponse = APIResponse | APIErrorResponse | null

export default function CreateOrderPage() {
  const API_URL = "http://127.0.0.1:5000";
  // const location = useLocation();
  const [orderResponse, setOrderResponse] = useState<orderResponse>(null)
  
  // Access the passed state via useNavigate() hook in AndrewBot.tsx for create 
  // order using useLocation() hook. 
  // const createOrderData = location.state.createOrderData.trim()

  useEffect(() => {
    // Directly access localStorage and parse the data
    const storedCreateOrderDetails = localStorage.getItem("createOrderDetails")?.trim();

    if (storedCreateOrderDetails) {
      localStorage.removeItem("createOrderDetails");
    }

    console.log("storedCreateOrderDetails: ", storedCreateOrderDetails);

    const createOrder = async (data : string) => {
      try {
        console.log("createOrderData:", data)
        const response = await axios.post(`${API_URL}/orders`, {
          // The API OrderManagementAPI will receive the order details in below format for POST API call.
          // The request will have "orderDetails" key added to it.
          // {
          //   "orderDetails":"wheat, ashirbaad, 5 kg, chatu, mana, 200 grams, rice flour, bb royal, 100 gms"
          // }
          orderDetails: data,
        });
        console.log(response);

        if (response.status === 200) {
          const APIResponse = response.data
          // console.log("API response:", APIResponse); // Log response data directly
          setOrderResponse(APIResponse); // Update state with response data
        } else {
            // Handle non-200 status codes
            console.error("Error: Received non-200 status code", response.status);
            // Optionally set an error state or handle the error
            setOrderResponse({ error: `Received status code ${response.status}` });
          }
        } catch (error) {
        console.log(error);
        setOrderResponse({ error: 'An error occurred while processing the request.' });
      }
    };

    // calling function createOrder() using createOrderData
    if (storedCreateOrderDetails) {
      createOrder(storedCreateOrderDetails);
    }
  }, []);

  // Process the response.data
  useEffect(() => {
    if (orderResponse && "tabs" in orderResponse) {
      const apiResponse = orderResponse as APIResponse; // Type assertion to APIResponse
      console.log("API response tabs:", apiResponse.tabs); // Access tabs from the API response
    }

  }, [orderResponse]);

  document.title = "AndrewBot - Create Order";

  return (
    <div>
      <h1>Create Order Page</h1>
      <p>Here you can create a new order.</p>
      {/* Add your form or content for creating an order here */}
    </div>
  );
}
function jsonify(orderDetails: string): any {
  throw new Error("Function not implemented.");
}
