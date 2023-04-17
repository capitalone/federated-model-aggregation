cd django-deployment
make compile-packages
make install
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     apt-get install redis;;
    Darwin*)    brew install redis;;
    CYGWIN*)    echo "Error! redis not supported by ${unameOut}"; exit 125;;
    MINGW*)     echo "Error! redis not supported by ${unameOut}"; exit 125;;
    *)          echo "Error! redis not supported by ${unameOut}"; exit 125;;
esac

