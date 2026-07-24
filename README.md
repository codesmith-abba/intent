# Intent Language (ITL)

> Programming by intention, not implementation.

Intent Language (ITL) is an experimental open-source programming language that enables developers to build applications by describing **what they want**, rather than manually implementing every file, component, API, and configuration.

Instead of writing hundreds of files across multiple frameworks, developers write **intent**, and the ITL compiler transforms that intent into complete applications.

---

## Imagine...

Imagine if programming worked like this:

Instead of creating:

- HTML
- CSS
- JavaScript
- React Components
- API Routes
- Database Models
- Authentication
- Storage
- Configuration files

...you simply described your application.

```itl
app $Portfolio {

    page $home {

        theme $dark

        hero $main {

            headline $Hi, I'm Abdulmumin

            subtitle $AI Engineer & Founder

            action $View Projects
        }

        section $about {}

        section $projects {}

        section $contact {}
    }

    target $web

    framework $react
}