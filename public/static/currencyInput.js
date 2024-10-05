export function currencyInput(elementID) {
    document.getElementById(elementID).addEventListener('input', function (e){
        let value = e.target.value;

        value = value.replace(/[^\d.]/g, '');

        if ((value.match(/\./g) || []).lengh > 1) {
            value = value.slice(0, value.lastIndexOf('.'));
        }

        if (value) {
            value = parseFlat(value).toFixed(2);
            e.target.value = `$${value.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        } else {
            e.target.value = '';
        }
    });
};