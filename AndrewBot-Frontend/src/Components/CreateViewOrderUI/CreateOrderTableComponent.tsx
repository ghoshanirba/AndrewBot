import React from 'react'

interface child {
    id: number;
    name: string;
    weight: string;
    magnitude: number;
    magnitude_unit: string;
    pricing: Pricing;
    brand: Brand;
    category: Category;
    keep_selected: string;
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

  interface CreateOrderTableComponentProps {
    children : child[]
  }
  
export default function CreateOrderTableComponent({ children }: CreateOrderTableComponentProps) {
  return (
    <div>
      <div className="table-responsive">
          <table className="table table-secondary table-striped table-bordered">
            <thead>
              <tr className="table-secondary">
                <th className="table-header-font" scope="col">
                  <input type="checkbox" id="selectAll" />
                </th>
                <th className="table-header-font" scope="col">
                  Product Name
                </th>
                <th className="table-header-font" scope="col">
                  Brand
                </th>
                <th className="table-header-font" scope="col">
                  Weight
                </th>
                <th className="table-header-font" scope="col">
                  Quantity
                </th>
                <th className="table-header-font" scope="col">
                  MRP Per Unit
                </th>
                {/* <th className="table-header-font" scope="col">
                  Total Price(MRP)
                </th> */}
                <th className="table-header-font" scope="col">
                  Discount Per Unit
                </th>
                {/* <th className="table-header-font" scope="col">
                  Total Discount
                </th> */}
                <th className="table-header-font" scope="col">
                  Selling Price Per Unit
                </th>
                {/* <th className="table-header-font" scope="col">
                  More Choices
                </th> */}
              </tr>
            </thead>
            <tbody>
              {children.map((child, index) => (
                <tr className="table table-striped" key={index}>
                  <td className="table-data-font">
                    <input type="checkbox" name="productSelect" value={child.id} />
                  </td>
                  <td className="table-data-font">{child.name}</td>
                  <td className="table-data-font">{child.brand.name}</td>
                  <td className="table-data-font">{child.weight}</td>
                  <td className="table-data-font">
                    <select className="form-select small-dropdown table-data-font">
                      <option selected value="1">1</option>
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
                  <td className="table-data-font">{child.pricing.mrp}</td>
                  {/* <td className="table-data-font">{1 * product.pricing.mrp}</td> */}
                  <td className="table-data-font">{child.pricing.discount}</td>
                  {/* <td className="table-data-font">1 * {product.pricing.discount}</td> */}
                  <td className="table-data-font">{child.pricing.selling_price}</td>
                  {/* <td className="table-data-font">Load More</td> */}
                </tr>
              ))}
            </tbody>
          </table>  
        </div> 
    </div>
  )
}
