console.log('2222', 2222)


const searchField = document.querySelector('#searchField');
const pagination_Container = document.querySelector('.pagin_container');
const table_Container = document.querySelector('#tableContainer');
const table_Output = document.querySelector('#tableOutput');
const tableBody = document.querySelector('.table-body');
const expenseId = document.querySelector('#pk_id');

tableOutput.style.display = 'none';

searchField.addEventListener('keyup', (e) => {
    const searchVal = e.target.value.trim();

    if (searchVal.length > 0) {
        pagination_Container.style.display = 'none';

        fetch("/search-expenses", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ searchText: searchVal })
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            console.log('data', data);
            table_Output.style.display = 'block';
            table_Container.style.display = 'none';

            if (data.length === 0) {
                tableBody.innerHTML = "<tr><td colspan='5'>No results found</td></tr>";
            } else {
                // Build HTML for table rows
                let html = '';
                data.forEach(item => {
                    // Generate edit and delete URLs
                    const editUrl = `/edit-expenses/${item.id}`; // Adjust the URL pattern according to your Django URL configuration
                    const deleteModalId = `deleteExpenseModal-${item.id}`;
                    const date = new Date(item.date);
                    const formattedDate = date.toISOString().split('T')[0]; // Format the date as YYYY-MM-DD

                    html += `
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.category}</td>
                            <td>${item.description}</td>
                            <td>${formattedDate}</td>
                            <td class="d-flex gap-2">
                                <a class="btn-outline-primary btn btn-sm" href="${editUrl}">Edit</a>
                                <button type="button" class="btn-danger btn btn-sm" data-bs-toggle="modal" data-bs-target="#${deleteModalId}">Delete</button>
                            </td>
                        </tr>
                        
                        <!-- Modal for Delete Confirmation -->
                        <div class="modal fade" id="${deleteModalId}" tabindex="-1" aria-labelledby="deleteExpenseModalLabel-${item.id}" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="deleteExpenseModalLabel-${item.id}">Confirm Delete</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        Are you sure you want to delete this expense?
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <a href="/delete-expenses/${item.id}" class="btn btn-danger">Delete</a>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                });

                // Update table body with built HTML
                tableBody.innerHTML = html;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    } else {
        table_Output.style.display = 'none';
        table_Container.style.display = 'block';
        pagination_Container.style.display = 'block';
    }
});

