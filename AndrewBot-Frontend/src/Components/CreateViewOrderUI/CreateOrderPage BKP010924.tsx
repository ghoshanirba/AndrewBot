import axios from "axios";
import React, { useEffect, useState, MouseEvent } from "react";
import { useLocation } from "react-router-dom";
import "./CreateOrderPage.css";
// import { Modal, Button } from "bootstrap";

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
  quantity?: number;
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

interface ProductModalProps {
  product: Product;
  onClose: () => void;
}

interface TableHeaderProps {
  lastColumnName: string;
}

interface TableRowProps {
  product: Product;
  showModal: boolean;
  parentOrChild: "parent" | "child";
}

interface userSelectedProducts {
  id: number;
  name: string;
  weight: string;
  magnitude: number;
  magnitude_unit: string;
  pricing: Pricing;
  brand: Brand;
  category: Category;
  keep_selected: string;
  quantity?: number;
}


export default function CreateOrderPage() {
  const API_URL = "http://127.0.0.1:5000";
  // const location = useLocation();
  const [orderResponse, setOrderResponse] = useState<APIResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState<string>("");
  const [loadMoreClicked, setLoadMoreClicked] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [userSelectedProducts, setUserSelectedProducts] = useState<userSelectedProducts[]>([]);
  const [newUserSelectedProducts, setNewUserSelectedProducts] = useState<Map<number, userSelectedProducts>>(new Map());
  
  // Get current date function
  const getCurrentDate = () => {
    const today = new Date();
    const formatDate = today.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
    console.log("formatDate:", formatDate);
    return formatDate;
  };

  //arrow function to handle the quantity changes
  // const handleQuantityChange = (product: Product) => {
  //   setQuantities((prevQuantities) => ({
  //     ...prevQuantities,
  //     [productID]: quantity,
  //   }));
  // };

  // const handleCheckBoxChange = (product: Product, checked: boolean) => {
  //   setUserSelectedProducts((prevUserSelectedProducts) => {
  //     const newUserSelectedProducts = new Map(prevUserSelectedProducts);

  //     if (checked) {
  //       newUserSelectedProducts.set(product.id, { ...product, quantity: 1 });
  //     } else {
  //       newUserSelectedProducts.delete(product.id);
  //     }
  //     return newUserSelectedProducts;
  //   });
  // };

  useEffect(() => {
    // Directly access localStorage and parse the data
    const storedCreateOrderDetails = localStorage
      .getItem("createOrderDetails")
      ?.trim();

    if (storedCreateOrderDetails) {
      localStorage.removeItem("createOrderDetails");
    }

    console.log("storedCreateOrderDetails: ", storedCreateOrderDetails);

    const composeOrder = async (orderDetails: string) => {
      try {
        console.log("composeOrderData:", orderDetails);

        const params = {
          orderDetails: orderDetails,
        };

        console.log("query params:", params);
        const response = await axios.get(`${API_URL}/orders/compose`, {
          // The API OrderManagementAPI will receive the order details in below format for GET API call.
          // The request will have "orderDetails" key added to it.
          // {
          //   "orderDetails":"wheat, ashirbaad, 5 kg, chatu, mana, 200 grams, rice flour, bb royal, 100 gms"
          // }
          params: params,
        });
        console.log(response);

        if (response.status === 200) {
          // console.log("API response:", response.data); // Log response data directly
          setOrderResponse(response.data); // Update state with response data
        } else {
          // Handle non-200 status codes
          console.error("Error: Received non-200 status code", response.status);
        }
      } catch (error) {
        setError("Error fetching order details");
        console.error("Error fetching order details:", error);
      } finally {
        setLoading(false);
      }
    };

    // Get the current date
    setCurrentDate(getCurrentDate());

    // calling function createOrder() using createOrderData
    if (storedCreateOrderDetails) {
      composeOrder(storedCreateOrderDetails);
    }
  }, []);

  // Process the response.data
  useEffect(() => {

    console.log("within order response useEffect hook")
    if (orderResponse && "tabs" in orderResponse) {
      const apiResponse = orderResponse as APIResponse; // Type assertion to APIResponse
      // console.log("API response tabs:", apiResponse.tabs.product_info); // Access tabs from the API response
      setProducts(apiResponse.tabs.product_info.products);

      const initialSelectedProducts : userSelectedProducts[] = apiResponse.tabs.product_info.products
      .filter(products => products.keep_selected === "Y")
      .map(products => ({
        id: products.id,
        name: products.name,
        weight: products.weight,
        magnitude: products.magnitude,
        magnitude_unit: products.magnitude_unit,
        pricing: products.pricing,
        brand: products.brand,
        category: products.category,
        keep_selected: products.keep_selected,
        quantity: 1,

      }))
      
      // Update userSelectedProducts with the array - these are the initial recommended choices
      setUserSelectedProducts(initialSelectedProducts)

      //Build a Map out of the initial recommended product choices
      const initialSelectedProductsMap = new Map<number, userSelectedProducts>(
        initialSelectedProducts.map(product => [product.id, product])
      );

      // Update newUserSelectedProducts with the Map
      setNewUserSelectedProducts(initialSelectedProductsMap)
      
    }
  }, [orderResponse]);

  console.log("1st userSelectedProducts:", userSelectedProducts)
  console.log("1st newUserSelectedProducts:", newUserSelectedProducts)

  // useEffect(() => {
  //   // Adding the select all functionality
  //   const selectAllCheckBox = document.getElementById("selectAll");

  //   if (selectAllCheckBox) {
  //     selectAllCheckBox.onclick = function () {
  //       let checkboxes = document.getElementsByName("productSelect");

  //       for (let checkbox of checkboxes) {
  //         if (
  //           checkbox instanceof HTMLInputElement &&
  //           checkbox.type === "checkbox"
  //         ) {
  //           (checkbox as HTMLInputElement).checked = (
  //             this as HTMLInputElement
  //           ).checked;
  //         }
  //       }
  //     };
  //   }
  // }, [products]);

  // Table Header Component
  function TableHeader({ lastColumnName }: TableHeaderProps) {
    return (
      <thead>
        <tr className="table-secondary">
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            <input type="checkbox" id="selectAll" />
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Product Name
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Brand
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Weight
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Quantity
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            MRP Per Unit
          </th>
          {/* <th className="table-header-font" scope="col">
                  Total Price(MRP)
                </th> */}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Discount Per Unit
          </th>
          {/* <th className="table-header-font" scope="col">
                  Total Discount
                </th> */}
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            Selling Price Per Unit
          </th>
          <th
            className="table-header-font"
            scope="col"
            style={{ textAlign: "center", verticalAlign: "middle" }}
          >
            {lastColumnName}
          </th>
        </tr>
      </thead>
    );
  }

  // Table Row Component
  function TableRow({ product, showModal, parentOrChild }: TableRowProps) {
    console.log("within TableRow component")
    console.log("product1:", product)
    // HTMLInputElement event for checkboxes
    // const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    //   handleCheckBoxChange(product, event.target.checked);
    // };

    const handleCheckBoxChange = (product: Product, checked: boolean) => {
      console.log("product2:", product)
      setNewUserSelectedProducts((prevUserSelectedProducts) => {
        //Create a Map from the previous state
        const updatedUserSelectedProducts = new Map(prevUserSelectedProducts);
  
        if (checked) {
          // If checked, add or update the product with its current quantity
          updatedUserSelectedProducts.set(product.id, { ...product, quantity: product.quantity || 1 });
        } else {
          // If unchecked, remove the product from the Map
          updatedUserSelectedProducts.delete(product.id);
        }

        // Convert the newUserSelectedProducts Map to an array, and update the userSelectedProducts state
        setUserSelectedProducts(Array.from(updatedUserSelectedProducts.values()));
       
        return updatedUserSelectedProducts;
      });
    };

    // HTMLSelectElement event for dropdown selects
    const handleQuantityChange = (
      product: Product,
      event: React.ChangeEvent<HTMLSelectElement>
    ) => {
          //event.target.value is a string. converting a string to base 10 integer
          console.log("product3:", product)
          const quantity = parseInt(event.target.value, 10);

          //Update the quantity in the products array
          setProducts((prevProducts) =>
            prevProducts.map((p) => 
              p.id === product.id ? {...p, quantity : quantity} : p
          )
        );

        // if (showModal) {
        //   setSelectedProduct((prevModalProducts) => {
        //     if (!prevModalProducts) return prevModalProducts;
        
        //     return prevModalProducts.map((p) =>
        //       p.id === product.id ? { ...p, quantity: quantity } : p
        //     );
        //   });
        // }

        if (newUserSelectedProducts.has(product.id)) {

          setNewUserSelectedProducts((prevUserSelectedProducts) => {
            const updatedUserSelectedProducts = new Map(prevUserSelectedProducts);
            updatedUserSelectedProducts.set(product.id, { ...product, quantity });
            
            setUserSelectedProducts(Array.from(updatedUserSelectedProducts.values()))
            
            return updatedUserSelectedProducts
          })
        }        
    };

    return (
      <tr className="table table-striped" key={product.id}>
        <td className="table-data-font">
          <input
            type="checkbox"
            name="productSelect"
            value={product.id}
            onChange={(event : React.ChangeEvent<HTMLInputElement>) => handleCheckBoxChange(product, event.target.checked)}
            checked={newUserSelectedProducts.has(product.id)}
          />
        </td>
        <td className="table-data-font">{product.name}</td>
        <td className="table-data-font">{product.brand.name}</td>
        <td className="table-data-font">{product.weight}</td>
        <td className="table-data-font">
          <select
            className="form-select small-dropdown table-data-font"
            value={product.quantity}
            onChange={(event) => handleQuantityChange(product, event)}
          >
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
            <option value="10">10</option>
          </select>
        </td>
        <td className="table-data-font">{product.pricing.mrp}</td>
        {/* <td className="table-data-font">{1 * product.pricing.mrp}</td> */}
        <td className="table-data-font">{product.pricing.discount}</td>
        {/* <td className="table-data-font">1 * {product.pricing.discount}</td> */}
        <td className="table-data-font">{product.pricing.selling_price}</td>
        <td className="table-data-font">
          {!showModal ? (
            <a
              href="#"
              onClick={(event) =>
                handleClickLoadMore(event, product, product.id)
              }
            >
              Load More
            </a>
          ) : product.keep_selected === "Y" ? (
            <span style={{ color: "#0d6efd" }}>Recommended</span>
          ) : (
            <span>Other Option</span>
          )}
        </td>
      </tr>
    );
  }


  const handleClickLoadMore = (
    event: React.MouseEvent<HTMLAnchorElement>,
    product: Product,
    index: number
  ) => {
    console.log("Within handleClickLoadMore");
    console.log("product:", product);
    event.preventDefault();
    setLoadMoreClicked(true);
    setSelectedProduct(product);
    setShowModal(true);
    console.log("Load more clicked");
  };

  // ProductModal is a Custom Modal Component
  function ProductModal({ product, onClose }: ProductModalProps) {
    console.log("Within showProductModal");
    console.log("product:", product);
    if (!product) return null;

    return (
      <div
        className="modal show d-block"
        tabIndex={-1}
        style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
      >
        <div className="modal-dialog modal-dialog-scrollable modal-xl">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{product.name}</h5>
              <button
                type="button"
                className="btn-close"
                aria-label="Close"
                onClick={onClose}
              ></button>
            </div>
            <div className="modal-body">
              <div className="table-responsive">
                <table className="table table-secondary table-striped table-bordered">
                  <TableHeader lastColumnName={"Options"} />
                  <tbody>
                    <TableRow
                      key={product.id}
                      product={product}
                      showModal={true}
                      parentOrChild="parent"
                    />

                    {product.children?.map((child) => (
                      <TableRow
                        key={child.id}
                        product={child}
                        showModal={true}
                        parentOrChild="child"
                      />
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Add other product details here */}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
              >
                Close
              </button>
              <button type="button" className="btn btn-primary">
                Save changes
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  
  document.title = "AndrewBot - Create Order";

  //Reset to initial state when the create order page 1st loaded.
  function handleReset(event: MouseEvent<HTMLButtonElement>): void {
    if (orderResponse) {
      setOrderResponse({ ...orderResponse });
    }    
  }

  function confirmOrder(event: MouseEvent<HTMLButtonElement, MouseEvent>): void {
    
    const isConfirmed = window.confirm("Are you sure you want to confirm the order ?");

    if(isConfirmed) {
      console.log("Order Confirmed!!!")
    } else {
      console.log("Order cancelled!!!")
    }
  }

  // console.log("products:", products)
  return (
    <>
      <nav className="navbar" style={{ backgroundColor: "#e3f2fd" }}>
        <div className="container-fluid">
          <div className="row w-100">
            <div className="col-6">
              <span className="navbar-brand mb-0 h1">
                AndrewBot - Create Order
              </span>
            </div>
            <div className="col-6 text-end pe-5">
              <span className="navbar-text font-monospace fw-semibold">
                User ID: ghoshanirban
                <br />
                Date: {currentDate}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        <p className="fs-5 fw-semibold text-center text-decoration-underline pt-3">
          Here You Can Edit/Modify Your Requested Orders
        </p>

        {/* Spinner showing Loading status*/}
        {loading ? (
          <div className="d-flex justify-content-center">
            <div className="spinner-border text-secondary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="table table-secondary table-striped table-bordered">
                <TableHeader lastColumnName={"More Options"} />

                <tbody>
                  {products.map((product, index) => (
                    <TableRow
                      key={product.id}
                      product={product}
                      showModal={false}
                      parentOrChild="parent"
                    />
                  ))}
                </tbody>
              </table>

              {selectedProduct && loadMoreClicked && showModal && (
                <ProductModal
                  product={selectedProduct}
                  onClose={() => {
                    setShowModal(false);
                    setLoadMoreClicked(false);
                  }}
                />
              )}
              
            </div>
            <div className="d-grid gap-2 d-md-flex justify-content-center">
              <button className="btn btn-secondary me-md-2" type="reset" value="Reset" onClick={handleReset}>Reset</button>
              <button className="btn btn-primary" type="button" onClick={confirmOrder}>Confirm</button>
            </div>
          </>
        )}
      </div>
    </>
  );
}
