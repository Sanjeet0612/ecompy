
function renderPagination(total, page, limit){

    let pages = Math.ceil(total / limit);
    let html = "";

    if(pages <= 1){
        $(".pagination-area").html("");
        return;
    }

    html += `<nav><ul class="pagination justify-content-end">`;

    for(let i = 1; i <= pages; i++){

        html += `
            <li class="page-item ${i == page ? 'active' : ''}">
                <a href="#" class="page-link pagination-btn" data-page="${i}">
                    ${i}
                </a>
            </li>
        `;
    }

    html += `</ul></nav>`;

    $(".pagination-area").html(html);
}

function renderRowsPerPageSelect(){
    let html = "";
    rowsPerPageOptions.forEach(val => {

        html += `
            <option value="${val}" ${val == currentLimit ? 'selected' : ''}>
                ${val}
            </option>
        `;
    });
    $("[data-table-set-rows-per-page]").html(html);
}
