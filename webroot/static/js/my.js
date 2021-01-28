/**
 *   (c) 2021 Yoichi Tanibayashi
 */

/**
 * @param {Date} d_from
 * @param {Date} d_to
 *
 * @return {number} days
 */
const calcDays = (d_from, d_to) => {
    const days = (d_to - d_from) / (24 * 60 * 60* 1000);
    return days;
};

/**
 * @param {Date} d
 * @param {number} days
 *
 * @return {Date} d
 */
const shiftDays = (d, days) => {
    d.setDate(d.getDate() + days);
    return d;
};

/**
 * `toLocaleDateString`が機能しない環境があるので、
 * あえて、面倒な変換を行う(!?)
 *
 * @param {Date} d
 *
 * @return {String} jst_str
 */
const getJSTString = (d) => {
    tz_msec = d.getTimezoneOffset() / 60 * 3600 * 1000;
    const jst_str = (new Date(d.getTime() - tz_msec)).toISOString();
    return jst_str;
};

/**
 * @param {Date} d
 *
 * @return {String} jst_date_str
 */
const getJSTDateString = (d) => {
    return getJSTString(d).replace(/T.*$/, '');
};

/**
 *
 */
const getTopDateString = () => {
    const el_date_from = document.getElementById("date_from");
    const el_date_to = document.getElementById("date_to");
    const win_top = window.pageYOffset;

    let el_date = document.getElementById(`date-${el_date_from.value}`);
    // console.log(`getTopDate: el_date.id=${el_date.id}`);
    while ( el_date.offsetTop < win_top ) {
        d1 = new Date(el_date.id.replace('date-',''));
        d1 = shiftDays(d1, 1);
        // console.log(`d1=${d1}`);
        d1_str = getJSTDateString(d1);
        el_date = document.getElementById(`date-${d1_str}`);
        // console.log(`getTopDate: el_date.id=${el_date.id}`);
    }
    return el_date.id.replace('date-', '');
};

/**
 * @return {number} days
 */
const getRelativeDate = () => {
    const top_date_str = getTopDateString();
    const d_top_date = new Date(top_date_str);
    const d_today = new Date(getJSTDateString(new Date()));
    const days = calcDays(d_today, d_top_date);
    return days;
};

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
    d1_str = getJSTDateString(d1);
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

/**
 *
 */
const scrollHdr = (event) => {
    const top_date_str = getTopDateString();
    const rel_days = getRelativeDate();
    // console.log(`rel_days=${rel_days}`);
    const el_rel_days = document.getElementById("rel_days");
    //el_rel_days.innerHTML = `${rel_days}`;
    yyyy_str = top_date_str.substr(0,4);
    mm_dd_str = top_date_str.substr(5,5).replace('-','/');
    sign_str = '';

    if (rel_days >= 0) {
        sign_str = '+';
    }
    el_rel_days.innerHTML = `${yyyy_str}<br />[${sign_str}${parseInt(rel_days/7)}w]`;

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
    if ( d_top < 200 ) {
        console.log(`scrollHdr:d_top=${d_top}`);
    }
    if ( d_bottom < 200 ) {
        console.log(`scrollHdr:d_bottom=${d_bottom}`);
    }
    
    if (d_top < 50) {
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

    const top_of_el = el.offsetTop;
    const bottom_of_el = el.offsetTop + el.offsetHeight;

    if (top_bottom == "bottom") {
        scrollTo({left: 0, top: bottom_of_el - win_h - 5,
                  behavior: behavior});
    } else {
       scrollTo({left: 0, top: top_of_el - 20,
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
    el_top_bottom.value = "top"; // set default to el_top_bottom

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
    d1 = shiftDays(d1, days);
    console.log(`moveDays:d1=${d1}`);

    d1_str = getJSTDateString(d1);
    console.log(`moveDays:d1_str=${d1_str}`);
    el.value = d1_str;
    scrollToDate(path, d1_str, behavior);
};

/**
 * [Important!]
 * スクロールによる自動読み込みより先に、自動読み込みをトリガー
 *
 * @param {number} direction
 * @param {String} path
 * @param {String} behavior
 */
const moveToMonday = (direction=1, path, behavior="smooth") => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${getJSTString(cur_day)}`);

    const wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }

    let days;
    let days2;
    if ( direction > 0 ) {
        days = 8 - wday;
        days2 = days + 21;
    } else {
        days = 1 - wday;
        if (days == 0) {
            days = -7; // Mon
        }
        days2 = days - 14;
    }
    console.log(`moveToMonday:days=${days}, days2=${days2}`);
    
    let d1 = new Date(el_cur_day.value);
    d1 = shiftDays(d1, days);
    d1_str = getJSTDateString(d1);
    console.log(`moveToMonday:d1_str=${d1_str}`);

    let d2 = new Date(el_cur_day.value);
    d2 = shiftDays(d2, days2);
    d2_str = getJSTDateString(d2);
    console.log(`moveToMonday:d2_str=${d2_str}`);

    el_d2 = document.getElementById(`date-${d2_str}`);
    if ( ! el_d2 ) {
        doPost(path, {date: d1_str});
        return;
    }

    el_cur_day.value = d1_str;
    scrollFlag = false;
    scrollToId(`date-${d1_str}`);
};

/**
 * TBD
 */
const editStr = (el0) => {
    console.log(`el0=${el0}`);
    let value = el0.innerHTML;
    console.log(`value=${value}`);
    const el_input = document.createElement("input");
    el_input.type="text";
    el_input.value = value;
    console.log(`el_input=${el_input.type}`);

    el0.replaceChildren(el_input);
    el0.onclick="";
    el0.onchange= () => {
        console.log(`value=${el_input.value}`);
    };
};
