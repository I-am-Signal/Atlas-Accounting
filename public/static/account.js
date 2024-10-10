export function clearCurrencyOfSymbols(currencyString) {
    return Number(String(currencyString)
        .replace(/[^0-9\.-]+/g, ""))
}


export function formatCurrency(currencyString) {
    return Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(
        clearCurrencyOfSymbols(currencyString)
    )
}


export function currencyInput(elementID) {
    // initial display of number
    document.getElementById(elementID).value = formatCurrency(
        document.getElementById(elementID).value
    )
    document.getElementById(elementID).addEventListener('blur', function (e) {
        // display of number after user exits box
        document.getElementById(elementID).value = formatCurrency(
            document.getElementById(elementID).value
        )
    });
};


// Logic for these functions may come in handly later for balancing monetary amounts, but not on the
// accounts screen
// export function ensureSidesAreBalancedWithELs(
//     normal_side_id,
//     balance_id,
//     debit_id,
//     credit_id
// ) {
//     [normal_side_id, balance_id]
//         .forEach(elementId => {
//             document.getElementById(elementId).addEventListener('blur', function () {
//                 ensureSidesAreBalanced(normal_side_id, balance_id, debit_id, credit_id, elementId);
//             });
//         });
// }


// function ensureSidesAreBalanced(
//     normal_side_id,
//     balance_id,
//     debit_id,
//     credit_id,
//     event_element_id
// ) {
//     const normalSide = document.getElementById(normal_side_id);
//     const balance = document.getElementById(balance_id);
//     const debit = document.getElementById(debit_id);
//     const credit = document.getElementById(credit_id);
//     const event_element = document.getElementById(event_element_id);

//     let bAmount = clearCurrencyOfSymbols(balance.value)
//     let dAmount = clearCurrencyOfSymbols(debit.value)
//     let cAmount = clearCurrencyOfSymbols(credit.value)

//     switch (event_element){
//         case balance:
//             // if balance is positive, add to Normal Side Dominant
//             // if balance is negative, add to Normal Side Subordinate
//             if (normalSide.value == 'Debit'){
//                 if (bAmount > 0){
//                     dAmount = bAmount - cAmount
//                 } else {
//                     cAmount = dAmount - bAmount
//                 }
//             }
            
//             // if balance is positive, add to Normal Side Dominant
//             // if balance is negative, add to Normal Side Subordinate
//             else{
//                 if (bAmount > 0){
//                     dAmount = cAmount - bAmount
//                 } else {
//                     cAmount = bAmount - dAmount
//                 }
//             }
//             break;

//         case debit:
//             // Normal Side Dominant
//             // balance = debit - credit
//             if (normalSide.value == 'Debit'){
//                 bAmount = dAmount - cAmount
//             }

//             // Normal Side Subordinate
//             // balance = credit - debit
//             else {
//                 bAmount = cAmount - dAmount
//             }
//             break;

//         case credit:
//             // Normal Side Dominant
//             // balance = credit - debit
//             if (normalSide.value == 'Credit'){
//                 bAmount = cAmount - dAmount
//             }
            
//             // Normal Side Subordinate
//             // balance = debit - credit
//             else {
//                 bAmount = dAmount - cAmount
//             }
//             break;
//     }   
//     // DEBIT IS DOMINANT
//     // debit has just been edited
//     //  balance = debit - credit
//     // credit has just been edited
//     //  balance = debit - credit
//     // balance has just been edited
//     //  debit = balance - credit

//     // CREDIT IS DOMINANT
//     // debit has just been edited
//     //  balance = credit - debit
//     // credit has just been edited
//     //  balance = credit - debit
//     // balance has just been edited
//     //  credit = balance - debit


//     balance.value = formatCurrency(bAmount);
//     debit.value = formatCurrency(dAmount);
//     credit.value = formatCurrency(cAmount);
// }