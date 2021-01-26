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

let scrollFlag = false;
const scrollHdr = (event) => {
    if ( ! scrollFlag ) {
        console.log(`scrollHdr:event=${event}, scrollFlag=${scrollFlag}`);
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
    console.log(`scrollHdr:${d_top}-${d_bottom}`);
    
    if (d_top < 70) {
        scrollFlag = false;
        el = document.getElementById("date_from");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, top_bottom: "top"});
    }
    if (d_bottom < 80) {
        scrollFlag = false;
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
    scrollFlag = false;
    console.log(`scrollToId:id=${id}`);
    
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

    scrollFlag = true;
    return true;
};

/**
 *
 */
const scrollToDate = (path, date, behavior = "smooth") => {
    scrollFlag = false;
    console.log(`scrollToDate:date=${date}`);
    
    const el_cur_day = document.getElementById("cur_day");
    const el_top_bottom = document.getElementById("top_bottom");
    const top_bottom = el_top_bottom.value;
    el_top_bottom.value = "top";

    if (scrollToId(`date-${date}`, top_bottom, behavior)) {
        el_cur_day.value = date;
        scrollFlag = true;
        return true;
    }

    console.log(`path=${path}`);
    doPost(path, {date: date});
    return false;
};

/*
 *
 */
const moveDays = (path, days, behavior="smooth") => {
    const el = document.getElementById("cur_day");
    let d1 = new Date(el.value);
    d1.setDate(d1.getDate() + days);
    console.log(`moveDays:d1=${d1}`);

    d1_str = d1.toISOString().replace(/T.*$/, '');
    el.value = d1_str;
    scrollToDate(path, d1_str, behavior);
};

/**
 *
 */
const moveToMonday = (direction=1, path, behavior="smooth") => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${cur_day}`);

    const wday = cur_day.getDay();

    let d_day;
    let d_day2;
    if ( direction > 0 ) {
        d_day = (1 - wday + 7) % 7;
        if (d_day == 0) {
            d_day = 7;
        }
        d_day2 = d_day + 21;
    } else {
        d_day = (1 - wday);
        if (d_day == 0) {
            d_day = -7;
        }
        if (d_day > 0) {
            d_day -= 7;
        }
        d_day2 = d_day - 21;
    }

    let d1 = new Date(el_cur_day.value);
    console.log(`d1=${d1}`);
    d1.setDate(d1.getDate() + d_day);
    console.log(`d1=${d1}`);
    d1_str = d1.toISOString().replace(/T.*$/, '');
    console.log(`moveToMonday:d1_str=${d1_str}`);

    let d2 = new Date(el_cur_day.value);
    d2.setDate(d2.getDate() + d_day2);
    d2_str = d2.toISOString().replace(/T.*$/, '');
    console.log(`moveToMonday:d2_str=${d2_str}`);

    el_d2 = document.getElementById(`date-${d2_str}`);
    if ( ! el_d2 ) {
        doPost(path, {date: d1_str});
    }

    el_cur_day.value = d1_str;
    scrollFlag = false;
    scrollToId(`date-${d1_str}`);
};
