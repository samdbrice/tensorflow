library(httr)
library(jsonlite)

HOME_DIR <- Sys.getenv("HOME")
BASE_URL <- "https://www.thedataincubator.com"
SECRET_GRADER_KEY <- "bcgzmGuIB9yAlmshSuLy"

load_url <- tryCatch({
    BASE_URL <- trimws(readLines(paste0(HOME_DIR, "/.ssh/.grader_url")))
}, warning = function(warn) {
    print(warn)
    print("WARNING encountered loading base URL. The base URL has still been changed.")
    BASE_URL <- trimws(readLines(paste0(HOME_DIR, "/.ssh/.grader_url")))
    return(NULL)
}, error = function(err) {
    print("ERROR encountered loading base URL. If you're developing, things will need to be seeded to the website.")
    print(err)
    return(NA)
})

load_key <- tryCatch({
    SECRET_GRADER_KEY <- trimws(readLines(paste0(HOME_DIR, "/.ssh/.grader_secret")))
}, warning = function(warn) {
    print(warn)
    print("WARNING encountered loading grader key. The key has still been changed.")
    SECRET_GRADER_KEY <- trimws(readLines(paste0(HOME_DIR, "/.ssh/.grader_secret")))
    return(NULL)
}, error = function(err) {
    print("ERROR: Problem loading grader key. Scores will still be reported, but not scored.")
    print("Please show this message to a TDI staff member.")
    print(err)
    return(NA)
})

is_invalid <- function(answer, type_str) {
    validation <- tryCatch({
        # get_validator(type_str).validate(answer)
        result <- NULL
    }, warning = function(warn) {
        return(warn)
    }, error = function(err) {
        return(err)
    })
    return(validation)
}

run_test_case <- function(func, test_case) {
    return(do.call(func, test_case$args))
}

test_cases_grading <- function(question_name, func, test_cases) {
    # Change this when we get rid of multiple test cases
    sub <- list()
    for (i in 1:nrow(test_cases)) {
        sub[[i]] <- run_test_case(func, test_cases[i,])
        validity <- is_invalid(sub[[i]], test_cases[i,]$type_str)
        if (!is.null(validity)) {
            print(validity)
            return(NULL)
        }
    }

    POST_URL <- paste0(BASE_URL, sprintf("/submission?api_key=%s", SECRET_GRADER_KEY))
    payload <- toJSON(list(question_name = question_name, submission = sub), dataframe = "values", factors = "string", auto_unbox = TRUE)
    resp <- POST(POST_URL, body = list(submission = payload))

    print("====================")
    if (status_code(resp) != 200) {
        print("Bad response from website")
    }

    score <- fromJSON(content(resp, "text"))
    if (score$error_msg != "") {
        print(paste0("Error: ", score$error_msg))
    } else {
        print(paste0("Your score: ", score$score))
    }
    print("====================")
}

score <- function(question_name, func) {

    # Get test cases
    GET_URL <- paste0(BASE_URL, sprintf("/test_cases/%s?api_key=%s", question_name, SECRET_GRADER_KEY))
    resp <- GET(GET_URL)
    if (status_code(resp) != 200) {
        print(paste0("No question found: ", question_name))
    }
    test_cases <- fromJSON(content(resp, "text"))
    test_cases_grading(question_name, func, test_cases)
}
