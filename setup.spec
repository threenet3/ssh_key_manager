Name:           python-ssh-key-manager
Version:        1.0.0
Release:        1%{?dist}
Summary:        Графическая утилита для управления SSH-ключами

License:        MIT
URL:            https://github.com/threenet3/ssh_key_manager
Source:         ssh-key-manager-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pillow)
BuildRequires:  python3dist(pyperclip)

%global _description %{expand:
SSH Key Manager — это графическая утилита для генерации, удаления и управления SSH-ключами
и конфигурацией ~/.ssh/config с помощью Tkinter. Предназначена для настольных пользователей Linux.}

%description %_description

%package -n python3-ssh-key-manager
Summary:        %{summary}
Recommends:     python3dist(pyperclip)
Recommends:     python3dist(pillow)

%description -n python3-ssh-key-manager %_description

%prep
%autosetup -n ssh-key-manager-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

# Название модуля
%pyproject_save_files ssh_key_manager

%files -n python3-ssh-key-manager -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/ssh-key-manager

%changelog
* Wed Jun 25 2025 Vsevolod <v.mikh3@gmail.com> - 1.0.0-1
- Initial build
