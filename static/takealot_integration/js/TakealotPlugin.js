document.addEventListener('DOMContentLoaded', function() {
  // The container element where the table will be inserted
  var container = document.getElementById('takealot-data-container');
  if (!container) {
    console.error('Container with id "takealot-data-container" not found');
    return;
  }

  // Show a basic loader while fetching data
  container.innerHTML = '<div id="loader">Loading...</div>';

  // Fetch the data from the endpoint
  fetch('/plugins/takealotintegrator/fetch-takealot-data/')
    .then(function(response) {
      return response.json();
    })
    .then(function(json) {
      // Remove the loader
      container.innerHTML = '';

      // Create the main table element
      var table = document.createElement('table');
      table.style.width = '100%';
      table.style.borderCollapse = 'collapse';
      table.style.border = '1px solid #ccc';

      // Build the header row
      var thead = document.createElement('thead');
      var headerRow = document.createElement('tr');
      var headers = ['', 'Image', 'Product Name', 'SDC', 'Sales'];
      headers.forEach(function(headerText) {
        var th = document.createElement('th');
        th.textContent = headerText;
        th.style.padding = '8px';
        th.style.border = '1px solid #ccc';
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Build the body of the table
      var tbody = document.createElement('tbody');

      // Loop through each product item in the data
      json.data.forEach(function(item) {
        // Main row
        var mainRow = document.createElement('tr');

        // Toggle button cell
        var toggleCell = document.createElement('td');
        toggleCell.style.padding = '8px';
        toggleCell.style.border = '1px solid #ccc';
        var toggleButton = document.createElement('button');
        toggleButton.textContent = '+';
        toggleButton.addEventListener('click', function() {
          var detailRow = document.getElementById('detail-' + item.sku);
          if (detailRow.style.display === 'none') {
            detailRow.style.display = '';
            toggleButton.textContent = '-';
          } else {
            detailRow.style.display = 'none';
            toggleButton.textContent = '+';
          }
        });
        toggleCell.appendChild(toggleButton);
        mainRow.appendChild(toggleCell);

        // Image cell
        var imageCell = document.createElement('td');
        imageCell.style.padding = '8px';
        imageCell.style.border = '1px solid #ccc';
        if (item.product_image) {
          var img = document.createElement('img');
          img.src = item.product_image;
          img.alt = item.product_name;
          img.width = 50;
          img.height = 50;
          imageCell.appendChild(img);
        } else {
          imageCell.textContent = 'N/A';
        }
        mainRow.appendChild(imageCell);

        // Product Name cell
        var nameCell = document.createElement('td');
        nameCell.style.padding = '8px';
        nameCell.style.border = '1px solid #ccc';
        nameCell.textContent = item.product_name;
        mainRow.appendChild(nameCell);

        // SDC cell
        var sdcCell = document.createElement('td');
        sdcCell.style.padding = '8px';
        sdcCell.style.border = '1px solid #ccc';
        sdcCell.textContent = item.sdc_total;
        mainRow.appendChild(sdcCell);

        // Sales Count cell
        var salesCell = document.createElement('td');
        salesCell.style.padding = '8px';
        salesCell.style.border = '1px solid #ccc';
        salesCell.textContent = item.sales_count;
        mainRow.appendChild(salesCell);

        tbody.appendChild(mainRow);

        // Collapsible detail row for warehouses
        var detailRow = document.createElement('tr');
        detailRow.id = 'detail-' + item.sku;
        detailRow.style.display = 'none';
        var detailCell = document.createElement('td');
        detailCell.colSpan = 5;
        detailCell.style.padding = '0';
        detailCell.style.border = '0';

        // Inner table for warehouse details
        var innerTable = document.createElement('table');
        innerTable.style.width = '100%';
        innerTable.style.borderCollapse = 'collapse';
        innerTable.style.border = '1px solid #ccc';

        // Inner table header
        var innerThead = document.createElement('thead');
        var innerHeaderRow = document.createElement('tr');
        ['Warehouse ID', 'Warehouse Name', 'SDC'].forEach(function(text) {
          var th = document.createElement('th');
          th.textContent = text;
          th.style.padding = '8px';
          th.style.border = '1px solid #ccc';
          innerHeaderRow.appendChild(th);
        });
        innerThead.appendChild(innerHeaderRow);
        innerTable.appendChild(innerThead);

        // Inner table body
        var innerTbody = document.createElement('tbody');
        item.warehouses.forEach(function(wh) {
          var whRow = document.createElement('tr');

          var whIdCell = document.createElement('td');
          whIdCell.textContent = wh.warehouse_id;
          whIdCell.style.padding = '8px';
          whIdCell.style.border = '1px solid #ccc';
          whRow.appendChild(whIdCell);

          var whNameCell = document.createElement('td');
          whNameCell.textContent = wh.warehouse_name;
          whNameCell.style.padding = '8px';
          whNameCell.style.border = '1px solid #ccc';
          whRow.appendChild(whNameCell);

          var whSdcCell = document.createElement('td');
          whSdcCell.textContent = wh.sdc;
          whSdcCell.style.padding = '8px';
          whSdcCell.style.border = '1px solid #ccc';
          whRow.appendChild(whSdcCell);

          innerTbody.appendChild(whRow);
        });
        innerTable.appendChild(innerTbody);

        detailCell.appendChild(innerTable);
        detailRow.appendChild(detailCell);
        tbody.appendChild(detailRow);
      });

      table.appendChild(tbody);
      container.appendChild(table);
    })
    .catch(function(err) {
      console.error("Error fetching data:", err);
      container.innerHTML = 'Error loading data';
    });
});