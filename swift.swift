// --- Valid Swift Code Examples ---

// 1. Variables and Constants
let constantInt: Int = 42
var variableString = "Hello, PLY"
let anotherConstant = 3.14 // Note: Float literals are currently parsed as ID in the simple grammar, but this is acceptable for a basic syntax validator.
var isTrue: Bool = true // Bool is treated as ID

// 2. Structures
struct SimpleStruct {
    let name: String = "Test"
    var count: Int = 0
}

// 3. Generics and Where Clause
protocol Hashable {}
protocol Comparable {}

struct GenericPair<T: Hashable, U> where T: Comparable {
    let first: T
    var second: U
}
// <T> typo placeholder ,T means the function work for any type 
// 4. Protocol (Minimal)
protocol MyProtocol {}

// 5. Nested Declarations (Structure containing a variable)
struct Outer {
    let innerConstant: Int = 100
}

// --- Invalid Swift Code Examples (For manual testing of error handling) ---

/*
// 1. Missing type after colon
let invalidVar: = 5

// 2. Missing RBRACE in struct
struct MissingBrace {
    let x: Int
// Missing '}'

// 3. Invalid generic constraint syntax (missing colon)
struct InvalidGeneric<T where T Comparable> {}

// 4. Invalid variable declaration (missing ID)
let : Int = 10
*/