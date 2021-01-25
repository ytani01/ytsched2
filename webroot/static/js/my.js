/**
 *   (c) 2021 Yoichi Tanibayashi
 */

/**
 *
 */
const doPost = (path, data) => {
    console.log(`doPost()`);

    const form = document.createElement("form");
    form.setAttribute("action", path);
    form.setAttribute("method", "POST");
    form.style.display = "none";
    document.body.appendChild(form);

    if (data !== undefined) {
        for (let param in data) {
            const input = document.createElement("input");
            input.setAttribute("type", "hidden");
            input.setAttribute("name", param);
            input.setAttribute("value", data[param]);
            form.appendChild(input);
        }
    }
    form.submit();
};

/**
 *
 */
const doPostDate = (path, date, days = 0) => {
    let d1 = new Date(date);
    d1.setDate(d1.getDate() + days);
    d1_str = d1.toISOString().replace(/T.*$/, '');
    console.log(`date=${date}, d1_str=${d1_str}`);

    doPost(path, {date: d1_str});
};

/**
 *
 */
const doGet = (path, data) => {
    let url = `${location.protocol}//${location.host}${path}?`;

    for (let param in data) {
        url += `${param}=${data[param]}&`;
    }
    url = url.replace(/&$/, '');
    console.log(`url=${url}`);
    window.location.href=url;
};

sc_flag = false;

const scroll_handler = (event) => {
    console.log(`event=${event}, sc_flag=${sc_flag}`);

    if ( ! sc_flag ) {
        return;
    }

    const el_search = document.getElementById("search_str");
    //console.log(`onscroll:search_str="${el_search.value}"`);
    if (el_search.value != "") {
        return;
    }

    const d_top = window.pageYOffset;
    const d_bottom = document.body.clientHeight - d_top
          - document.documentElement.clientHeight;
    console.log(`${d_top}-${d_bottom}`);
    
    if (d_top < 70) {
        sc_flag = false;
        el = document.getElementById("date_from");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, top_bottom: "top"});
    }
    if (d_bottom < 90) {
        sc_flag = false;
        el = document.getElementById("date_to");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, top_bottom: "bottom"});
    }
};

/**
 *
 */
const scrollToId = (id, top_bottom = "top", behavior = "smooth") => {
    sc_flag = false;
    console.log(`id=${id}`);
    
    const body_h = document.body.clientHeight;
    const win_h = document.documentElement.clientHeight;

    if (body_h <= win_h) {
        console.log(`body_h=${body_h} < win_h=${win_h}`);
        return true;
    }

    const el = document.getElementById(id);
    const el_search = document.getElementById('search_str');
    const search_str = el_search.value;

    if (el == null) {
        console.log(`scrollToId:scrollToID:el=${el}`);

        if (search_str) {
            return true;
        }
        return false;
    }

    const top_id = el.offsetTop;
    const bottom_id = el.offsetTop + el.offsetHeight;

    if (top_bottom == "bottom") {
        scrollTo({left: 0, top: bottom_id - win_h + 3,
                  behavior: behavior});
    } else {
        scrollTo({left: 0, top: top_id - 70,
                  behavior: behavior});
    }

    sc_flag = true;

    return true;
};

/**
 *
 */
const scrollToDate = (path, date, behavior = "smooth") => {
    sc_flag = false;
    
    console.log(`scrollToDate:date=${date}`);
    const el_top_bottom = document.getElementById("top_bottom");
    const top_bottom = el_top_bottom.value;
    el_top_bottom.value = "top";

    if (scrollToId(`date-${date}`, top_bottom, behavior)) {
        sc_flag = true;
    
        return true;
    }

    doPost(path, {date: date});
    return false;
};

/**
 *
 */
const moveDays = (path, days, behavior = "smooth") => {
    const el = document.getElementById("cur_day");
    let d1 = new Date(el.value);
    d1.setDate(d1.getDate() + days);
    console.log(`d1=${d1}`);

    d1_str = d1.toISOString().replace(/T.*$/, '');
    scrollToDate(path, d1_str, behavior);
};
