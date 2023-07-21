export const pluck = (elements, field) => {
    return elements.map((element) => element[field])
}