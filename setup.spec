Name:           python-ssh-key-manager
Version:        1.0
Release:        1%{?dist}
Summary:        Графическая утилита для управления SSH ключами

License:        MIT
URL:            https://github.com/threenet3/ssh_key_manager
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Прямые зависимости
Requires:       python3 >= 3.8
Requires:       python3-tkinter
Requires:       python3-pyperclip
Requires:       python3-pillow
Requires:       openssh-clients

%global _description %{expand:
Графическое приложение на Python с интерфейсом Tkinter для создания, удаления и управления SSH-ключами,
а также редактирования ~/.ssh/config.}

%description %_description

%package -n python3-ssh-key-manager
Summary:        %{summary}
%description -n python3-ssh-key-manager %_description

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

# Установка иконки и скрипта запуска вручную
mkdir -p %{buildroot}/usr/share/%{name}/assets
cp assets/ssh.png %{buildroot}/usr/share/%{name}/assets/

mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/ssh-key-manager <<EOF
#!/bin/bash
exec python3 -m ssh_key_manager "\$@"
EOF
chmod +x %{buildroot}/usr/bin/ssh-key-manager

%pyproject_save_files ssh_key_manager

%files -n python3-ssh-key-manager -f %{pyproject_files}
/usr/bin/ssh-key-manager
/usr/share/%{name}/assets/ssh.png
%doc README.md
%license LICENSE

%changelog
* Wed Jun 25 2025 Vsevolod <v.mikh3@gmail.com> - 1.0-1
- Initial RPM build using pyproject macros
