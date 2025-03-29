// static/inventree_takealot/js/TakealotPlugin.js
import React, { useState, useEffect } from 'react';
import { Table, Image, Collapse, Button, Loader } from '@mantine/core';
import { IconPlus, IconMinus } from '@tabler/icons-react';

function TakealotPlugin() {
  const [data, setData] = useState([]);
  const [expandedRows, setExpandedRows] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/plugin/takealotintegrator/fetch-takealot-data/')
      .then(response => response.json())
      .then(json => {
        setData(json.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching data:", err);
        setLoading(false);
      });
  }, []);

  const toggleRow = (sku) => {
    setExpandedRows(prev => ({
      ...prev,
      [sku]: !prev[sku]
    }));
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <Table striped highlightOnHover>
      <thead>
        <tr>
          <th></th>
          <th>Image</th>
          <th>Product Name</th>
          <th>SDC</th>
          <th>Sales</th>
        </tr>
      </thead>
      <tbody>
        {data.map(item => (
          <React.Fragment key={item.sku}>
            <tr>
              <td>
                <Button variant="subtle" onClick={() => toggleRow(item.sku)}>
                  {expandedRows[item.sku] ? <IconMinus size={16} /> : <IconPlus size={16} />}
                </Button>
              </td>
              <td>
                {item.product_image ? (
                  <Image src={item.product_image} alt={item.product_name} width={50} height={50} />
                ) : (
                  'N/A'
                )}
              </td>
              <td>{item.product_name}</td>
              <td>{item.sdc_total}</td>
              <td>{item.sales_count}</td>
            </tr>
            <tr>
              <td colSpan={5} style={{ padding: 0, border: 0 }}>
                <Collapse in={expandedRows[item.sku]}>
                  <Table>
                    <thead>
                      <tr>
                        <th>Warehouse ID</th>
                        <th>Warehouse Name</th>
                        <th>SDC</th>
                      </tr>
                    </thead>
                    <tbody>
                      {item.warehouses.map((wh, idx) => (
                        <tr key={idx}>
                          <td>{wh.warehouse_id}</td>
                          <td>{wh.warehouse_name}</td>
                          <td>{wh.sdc}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Collapse>
              </td>
            </tr>
          </React.Fragment>
        ))}
      </tbody>
    </Table>
  );
}

window.TakealotPlugin = TakealotPlugin;