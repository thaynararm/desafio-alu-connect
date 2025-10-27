from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Permite acesso apenas a usuários ADMIN."""
    def has_permission(self, request, view):
        return request.user.profile == "ADMIN"

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Permite acesso a ADMIN ou ao próprio INSTRUCTOR.
    Instrutores só podem acessar seus próprios registros.
    """
    def has_permission(self, request, view):
        if request.user.profile == "ADMIN":
            return True
        if hasattr(request.user, 'user_instructor'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.profile == "ADMIN":
            return True

        if hasattr(request.user, "user_instructor"):
            if hasattr(obj, "user"):
                return obj.user == request.user
            elif hasattr(obj, "instructors"):
                return obj.instructors.filter(user=request.user).exists()
            elif hasattr(obj, "course"):
                return obj.course.instructors.filter(user=request.user).exists()

        return False

class IsStudentOrAdmin(permissions.BasePermission):
    """
    Permite acesso a ADMIN ou ao próprio STUDENT.
    Estudantes só podem acessar seus próprios registros.
    """
    def has_permission(self, request, view):
        if request.user.profile == "ADMIN":
            return True
        if hasattr(request.user, 'user_student'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.profile == "ADMIN":
            return True
        if hasattr(request.user, 'user_student'):
            return obj.user == request.user
        return False

class IsAdminOrInstructorOrStudent(permissions.BasePermission):
    """
    Permite acesso a ADMIN, ou ao próprio INSTRUCTOR/STUDENT.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.profile == "ADMIN":
            return True
        return obj == request.user
