get_templates () {
    local -n arr=$1
    # for key in "${!arr[@]}"; do
    #     echo "${key}" "${arr[${key}]}"
    # done
    directories_before=$(find . -maxdepth 1 -type d)
    git clone "${arr["ssh_url"]}"
    directories_after=$(find . -maxdepth 1 -type d)

    cloned_directory=$(comm -13 <(echo "$directories_before") <(echo "$directories_after"))
    echo "The repository was cloned into: $cloned_directory"
    copied=$(ls "$cloned_directory")
    mv "$cloned_directory/$copied" "${arr["filename"]}"
    rm -rf "$cloned_directory"
}

declare -A pyproject_template
pyproject_template+=(["ssh_url"]="git@gitlab.com:snippets/3736540.git" ["filename"]="pyproject.toml")

declare -A flake8_template
flake8_template+=(["ssh_url"]="git@gitlab.com:snippets/3736539.git" ["filename"]=".flake8")

declare -A precommit_template
precommit_template+=(["ssh_url"]="git@gitlab.com:snippets/3736547.git" ["filename"]=".pre-commit-config.yaml")


if [ $# -eq 0 ]; then
    echo "No arguments provided, cloning all templates..."
    get_templates pyproject_template
    get_templates flake8_template
    get_templates precommit_template
else
    # Iterate over all provided arguments
    for arg in "$@"; do
        case $arg in
            pyproject)
                get_templates pyproject_template
                ;;
            flake8)
                get_templates flake8_template
                ;;
            precommit)
                get_templates precommit_template
                ;;
            *)
                echo "Unknown template: $arg"
                echo "Available templates are:" 
                echo " - pyproject"
                echo " - flake8"
                echo " - precommit"
                ;;
        esac
    done
fi

mkdir src tests
touch src/main.py
touch tests/test_main.py

echo "import pytest
from src.main import hello

def test_print_statement(capfd):
    hello()
    out, err = capfd.readouterr()
    assert \"x\" in out" > tests/test_main.py

